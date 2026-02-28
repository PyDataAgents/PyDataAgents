from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class PDFWriteFormAction(BufferNode, Action):
    """Write LLM- or user-provided values into PDF AcroForm fields using PyMuPDF."""

    path_input_keys: list[str] = field(default_factory=lambda: ["values", "filepath", "pdf_path"])
    fill_input_keys: list[str] = field(
        default_factory=lambda: ["answer", "answers", "fields", "field_values", "llm_data", "content"]
    )
    row_mode: str = field(default="per_pdf")
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "output_filepath", "written_fields", "written_field_count"]
    )
    output_folder: str | None = field(default="resources/Outputs")
    output_suffix: str = field(default="_filled")
    overwrite_source: bool = field(default=False)
    flatten: bool = field(default=False)
    strict_unknown_fields: bool = field(default=True)
    require_pdf_extension: bool = field(default=True)

    def _on_install(self, agent: Agent = None):
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        if len(self.output_keys) != 4:
            raise NodeException(f"{self.cname()} requires exactly 4 output_keys, got {len(self.output_keys)}")
        if self.row_mode not in {"per_pdf", "per_field"}:
            raise NodeException("row_mode must be either 'per_pdf' or 'per_field'")
        if self.overwrite_source and self.output_folder is not None:
            raise NodeException("output_folder cannot be set when overwrite_source=True")
        if len(self.path_input_keys) == 0:
            raise NodeException("path_input_keys must not be empty")
        if len(self.fill_input_keys) == 0:
            raise NodeException("fill_input_keys must not be empty")

    def _on_execute(self):
        parent_data = self.get_parent_data()
        if not parent_data:
            raise NodeException("No parent data was found")

        file_paths = self._extract_paths_from_parent_data(parent_data)
        if len(file_paths) == 0:
            raise NodeException("No PDF file paths were found in parent buffer data")

        payloads_by_path = self._extract_payloads_by_path(parent_data)
        sequential_payloads = self._extract_fill_payloads(parent_data)
        sequential_payloads = self._normalize_sequential_payloads(
            sequential_payloads=sequential_payloads,
            file_paths=file_paths,
            has_payloads_by_path=len(payloads_by_path) > 0,
        )

        if len(payloads_by_path) == 0 and len(sequential_payloads) == 0:
            raise NodeException("No valid filled form payloads were found in parent buffer data")

        iteration_paths = self._dedupe_paths(file_paths) if len(payloads_by_path) > 0 else list(file_paths)
        if len(payloads_by_path) == 0 and len(sequential_payloads) not in {1, len(iteration_paths)}:
            raise NodeException(
                "Number of fill payloads ("
                + str(len(sequential_payloads))
                + ") must be 1 or equal to number of PDF paths ("
                + str(len(iteration_paths))
                + ")"
            )

        for idx, file_path in enumerate(iteration_paths):
            self._validate_pdf_path(file_path)

            field_values = payloads_by_path.get(file_path)
            if field_values is None:
                if len(sequential_payloads) == 1:
                    field_values = sequential_payloads[0]
                elif len(sequential_payloads) == len(iteration_paths):
                    field_values = sequential_payloads[idx]
                else:
                    raise NodeException("No matching fill payload found for filepath " + str(file_path))

            output_path = self._resolve_output_path(file_path)
            written_fields = self._write_pdf(file_path, output_path, field_values)

            row = dict(
                zip(
                    self.output_keys,
                    [file_path, output_path, written_fields, len(written_fields)],
                )
            )
            self.add_data({key: [value] for key, value in row.items()})

    def _validate_pdf_path(self, file_path: str):
        if not FileUtils.exists_file(file_path):
            raise NodeException("filepath " + str(file_path) + " does not exist")
        if self.require_pdf_extension and not str(file_path).lower().endswith(".pdf"):
            raise NodeException("filepath " + str(file_path) + " is not a PDF file")

    def _extract_paths_from_parent_data(self, data: dict[str, Any]) -> list[str]:
        keys = self.path_input_keys if len(self.path_input_keys) > 0 else list(data.keys())
        paths: list[str] = []
        for key in keys:
            if key in data:
                self._collect_paths(data[key], paths)
        return paths

    def _collect_paths(self, value: Any, target: list[str]):
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned == "":
                raise NodeException("empty file path in parent data")
            target.append(cleaned)
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect_paths(item, target)
            return
        raise NodeException("unsupported parent data type for file path extraction: " + str(type(value)))

    def _extract_payloads_by_path(self, data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        mapping: dict[str, dict[str, Any]] = {}
        path_keys = ["filepath", "file_path", "pdf_path", "pdf"]
        present_path_keys = [key for key in path_keys if key in data]
        present_fill_keys = [key for key in self.fill_input_keys if key in data]

        for path_key in present_path_keys:
            path_values = self._as_list(data[path_key])
            if len(path_values) == 0:
                continue
            for fill_key in present_fill_keys:
                fill_values = self._as_list(data[fill_key])
                if len(fill_values) == 0:
                    continue
                row_count = min(len(path_values), len(fill_values))
                for idx in range(row_count):
                    path = self._try_extract_single_path(path_values[idx])
                    if path is None:
                        continue
                    normalized = self._normalize_payload(fill_values[idx])
                    if normalized is None or len(normalized) == 0:
                        continue
                    existing = mapping.get(path, {})
                    mapping[path] = self._merge_field_values(existing, normalized)
        return mapping

    def _extract_fill_payloads(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        keys = self.fill_input_keys if len(self.fill_input_keys) > 0 else list(data.keys())
        candidates: list[Any] = []
        for key in keys:
            if key in data:
                self._collect_payload_candidates(data[key], candidates)

        payloads: list[dict[str, Any]] = []
        for candidate in candidates:
            normalized = self._normalize_payload(candidate)
            if normalized is not None and len(normalized) > 0:
                payloads.append(normalized)
        return payloads

    def _collect_payload_candidates(self, value: Any, target: list[Any]):
        if value is None:
            return
        if isinstance(value, (str, dict)):
            target.append(value)
            return
        if isinstance(value, (list, tuple)):
            if self._looks_like_field_list(value):
                target.append(list(value))
                return
            for item in value:
                self._collect_payload_candidates(item, target)
            return
        target.append(value)

    def _looks_like_field_list(self, value: Any) -> bool:
        if not isinstance(value, (list, tuple)) or len(value) == 0:
            return False
        if not all(isinstance(item, dict) for item in value):
            return False
        return any(("field_name" in item or "field_id" in item or "write_target_field_id" in item) for item in value)

    def _looks_like_field_item(self, payload: dict[str, Any]) -> bool:
        has_field = any(
            key in payload and str(payload.get(key)).strip() != ""
            for key in ["field_name", "write_target_field_id", "field_id"]
        )
        has_value = any(
            key in payload
            for key in ["determined_value", "field_value", "value", "current_value", "proposed_value", "answer"]
        )
        return has_field and has_value

    def _normalize_payload(self, payload: Any) -> dict[str, Any] | None:
        if payload is None:
            return None

        if isinstance(payload, str):
            parsed = self._parse_payload_text(payload)
            if parsed is None:
                return None
            return self._normalize_payload(parsed)

        if isinstance(payload, (list, tuple)):
            if self._looks_like_field_list(payload):
                return self._normalize_field_list(payload)
            merged: dict[str, Any] = {}
            for item in payload:
                normalized = self._normalize_payload(item)
                if normalized is not None and len(normalized) > 0:
                    merged = self._merge_field_values(merged, normalized)
            return merged if len(merged) > 0 else None

        if isinstance(payload, dict):
            merged_wrappers: dict[str, Any] = {}
            for wrapper_key in [
                "fields",
                "field_values",
                "llm_data",
                "content",
                "answer",
                "answers",
                "values",
                "data",
            ]:
                if wrapper_key in payload:
                    normalized = self._normalize_payload(payload[wrapper_key])
                    if normalized is not None and len(normalized) > 0:
                        merged_wrappers = self._merge_field_values(merged_wrappers, normalized)
            if len(merged_wrappers) > 0:
                return merged_wrappers

            if self._looks_like_field_item(payload):
                return self._normalize_field_item(payload)

            result: dict[str, Any] = {}
            skip_keys = {
                "filepath",
                "file_path",
                "pdf_path",
                "pdf",
                "metadata",
                "full_text_content",
                "llm_prompt",
                "field_name",
                "field_type",
                "tooltip",
                "visual_label",
                "page_context",
                "page_index",
                "rect",
                "is_writable",
                "button_states",
            }
            for key, value in payload.items():
                if key in skip_keys:
                    continue
                if isinstance(value, (dict, list, tuple)):
                    nested = self._normalize_payload(value)
                    if nested is not None and len(nested) > 0:
                        result = self._merge_field_values(result, nested)
                    continue
                result[str(key)] = self._normalize_write_value(value)
            return result if len(result) > 0 else None

        return None

    def _normalize_field_list(self, payload: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any] | None:
        result: dict[str, Any] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            normalized = self._normalize_field_item(item)
            if normalized is None:
                continue
            result = self._merge_field_values(result, normalized)
        return result if len(result) > 0 else None

    def _normalize_field_item(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if payload.get("is_writable") is False:
            return None

        target = self._resolve_field_target(payload)
        if target is None:
            return None

        value = self._resolve_field_value(payload)
        if value is None:
            value = ""
        return {target: self._normalize_write_value(value)}

    def _resolve_field_target(self, payload: dict[str, Any]) -> str | None:
        for key in ["field_name", "write_target_field_id", "field_id"]:
            value = payload.get(key)
            if value is None:
                continue
            cleaned = str(value).strip()
            if cleaned != "":
                return cleaned
        return None

    def _resolve_field_value(self, payload: dict[str, Any]) -> Any:
        for key in ["determined_value", "field_value", "value", "current_value", "proposed_value", "answer"]:
            if key in payload:
                return payload.get(key)
        return None

    def _parse_payload_text(self, text: str) -> Any:
        clean = str(text).strip()
        if clean == "":
            return None

        if clean.startswith("```"):
            lines = clean.splitlines()
            if len(lines) >= 2:
                lines = lines[1:]
                if len(lines) > 0 and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                clean = "\n".join(lines).strip()

        try:
            return json.loads(clean)
        except Exception:
            pass

        object_start = clean.find("{")
        object_end = clean.rfind("}")
        if object_start >= 0 and object_end > object_start:
            try:
                return json.loads(clean[object_start : object_end + 1])
            except Exception:
                pass

        list_start = clean.find("[")
        list_end = clean.rfind("]")
        if list_start >= 0 and list_end > list_start:
            try:
                return json.loads(clean[list_start : list_end + 1])
            except Exception:
                pass
        return None

    def _normalize_sequential_payloads(
        self,
        sequential_payloads: list[dict[str, Any]],
        file_paths: list[str],
        has_payloads_by_path: bool,
    ) -> list[dict[str, Any]]:
        if self.row_mode == "per_pdf":
            return sequential_payloads
        if has_payloads_by_path:
            return sequential_payloads
        if len(sequential_payloads) == 0:
            return []

        if len(file_paths) == 1:
            merged: dict[str, Any] = {}
            for payload in sequential_payloads:
                merged = self._merge_field_values(merged, payload)
            return [merged] if len(merged) > 0 else []

        if len(sequential_payloads) in {1, len(file_paths)}:
            return sequential_payloads

        raise NodeException(
            "row_mode='per_field' requires filepath mapping for multiple PDFs, or exactly one payload per filepath"
        )

    def _resolve_output_path(self, source_path: str) -> str:
        if self.overwrite_source:
            return source_path
        source = Path(source_path)
        folder = source.parent if self.output_folder is None else Path(self.output_folder)
        output_name = source.stem + self.output_suffix + source.suffix
        return str(folder / output_name)

    def _write_pdf(self, source_path: str, output_path: str, field_values: dict[str, Any]) -> dict[str, Any]:
        fitz = self._import_fitz()
        try:
            document = fitz.open(source_path)
        except Exception as exc:
            raise NodeException("could not read pdf file " + str(source_path)) from exc

        try:
            widgets_by_field = self._index_widgets(document)
            unknown_fields = [name for name in field_values.keys() if name not in widgets_by_field]
            if self.strict_unknown_fields and len(unknown_fields) > 0:
                raise NodeException("unknown PDF field(s): " + ", ".join(sorted(unknown_fields)))

            writable_values = {k: v for k, v in field_values.items() if k in widgets_by_field}
            written_fields: dict[str, Any] = {}
            for field_name, value in writable_values.items():
                widgets = widgets_by_field.get(field_name, [])
                applied_value = self._write_field_to_widgets(field_name, widgets, value, fitz)
                written_fields[field_name] = applied_value

            if self.flatten:
                self._flatten_document(document)

            target_folder = FileUtils.parent_folder(output_path)
            if target_folder != "":
                FileUtils.create_dir(target_folder)

            self._save_document(document, source_path, output_path)
            return written_fields
        except NodeException:
            raise
        except Exception as exc:
            raise NodeException("could not write pdf file " + str(output_path)) from exc
        finally:
            document.close()

    def _index_widgets(self, document: Any) -> dict[str, list[Any]]:
        widgets_by_field: dict[str, list[Any]] = {}
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            widgets = page.widgets()
            if widgets is None:
                continue
            for widget in widgets:
                field_name = self._clean_text(str(getattr(widget, "field_name", "") or ""))
                if field_name == "":
                    continue
                widgets_by_field.setdefault(field_name, []).append(widget)
        return widgets_by_field

    def _write_field_to_widgets(self, field_name: str, widgets: list[Any], value: Any, fitz: Any) -> Any:
        if len(widgets) == 0:
            raise NodeException("No widgets found for field " + str(field_name))

        widget_types = [self._classify_widget_type(widget, fitz) for widget in widgets]
        writable_types = [kind for kind in widget_types if kind in {"text", "dropdown", "listbox", "checkbox", "radio"}]
        if len(writable_types) == 0:
            raise NodeException("Field " + str(field_name) + " is not writable")

        if all(kind in {"checkbox", "radio"} for kind in writable_types):
            return self._write_button_group(widgets, value)

        if any(kind in {"checkbox", "radio"} for kind in writable_types):
            raise NodeException("Mixed button/text widget group is unsupported for field " + str(field_name))

        text_value = self._to_text_field_value(value)
        for widget in widgets:
            kind = self._classify_widget_type(widget, fitz)
            if kind not in {"text", "dropdown", "listbox"}:
                continue
            widget.field_value = text_value
            widget.update()
        return text_value

    def _write_button_group(self, widgets: list[Any], value: Any) -> str:
        union_states = self._collect_group_states(widgets)
        target_state = self._resolve_target_button_state(value, union_states)
        target_key = target_state.lower()

        for widget in widgets:
            widget_states = self._collect_button_states(widget)
            lookup = {state.lower(): state for state in widget_states}
            off_state = self._resolve_off_state(widget_states)
            write_state = lookup.get(target_key, off_state)
            widget.field_value = write_state
            widget.update()
        return target_state

    def _collect_group_states(self, widgets: list[Any]) -> list[str]:
        states: list[str] = []
        seen: set[str] = set()
        for widget in widgets:
            for state in self._collect_button_states(widget):
                low = state.lower()
                if low in seen:
                    continue
                seen.add(low)
                states.append(state)
        if "off" not in {item.lower() for item in states}:
            states.append("Off")
        return states

    def _resolve_target_button_state(self, value: Any, available_states: list[str]) -> str:
        if len(available_states) == 0:
            raise NodeException("No button states available")

        state_lookup = {state.lower(): state for state in available_states}
        off_state = self._resolve_off_state(available_states)
        on_candidates = [state for state in available_states if state.lower() != off_state.lower()]

        if isinstance(value, str):
            cleaned = self._normalize_state_name(value)
            lowered = cleaned.lower()
            if lowered in state_lookup:
                return state_lookup[lowered]
            truthy = {"1", "true", "yes", "on", "x", "checked", "selected", "ja"}
            falsy = {"0", "false", "no", "off", "unchecked", "none", ""}
            if lowered in truthy:
                if len(on_candidates) == 0:
                    raise NodeException("No ON-state found for button field")
                return on_candidates[0]
            if lowered in falsy:
                return off_state
            raise NodeException("Could not map button value '" + str(value) + "' to available states")

        if isinstance(value, bool):
            if value:
                if len(on_candidates) == 0:
                    raise NodeException("No ON-state found for button field")
                return on_candidates[0]
            return off_state

        if isinstance(value, (int, float)):
            if float(value) == 0.0:
                return off_state
            if len(on_candidates) == 0:
                raise NodeException("No ON-state found for button field")
            return on_candidates[0]

        if value is None:
            return off_state

        normalized = self._normalize_state_name(str(value)).lower()
        if normalized in state_lookup:
            return state_lookup[normalized]
        raise NodeException("Could not map button value '" + str(value) + "' to available states")

    def _resolve_off_state(self, states: list[str]) -> str:
        for state in states:
            if state.lower() == "off":
                return state
        return "Off"

    def _to_text_field_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        if isinstance(value, (dict, list, tuple)):
            try:
                return json.dumps(value, ensure_ascii=True)
            except Exception:
                return str(value)
        return str(value)

    def _classify_widget_type(self, widget: Any, fitz: Any) -> str:
        code = getattr(widget, "field_type", None)
        mapping = {
            getattr(fitz, "PDF_WIDGET_TYPE_TEXT", object()): "text",
            getattr(fitz, "PDF_WIDGET_TYPE_CHECKBOX", object()): "checkbox",
            getattr(fitz, "PDF_WIDGET_TYPE_RADIOBUTTON", object()): "radio",
            getattr(fitz, "PDF_WIDGET_TYPE_COMBOBOX", object()): "dropdown",
            getattr(fitz, "PDF_WIDGET_TYPE_LISTBOX", object()): "listbox",
            getattr(fitz, "PDF_WIDGET_TYPE_SIGNATURE", object()): "signature",
        }
        if code in mapping:
            return mapping[code]

        type_string = str(getattr(widget, "field_type_string", "") or "").lower()
        if "text" in type_string:
            return "text"
        if "check" in type_string:
            return "checkbox"
        if "radio" in type_string:
            return "radio"
        if "combo" in type_string:
            return "dropdown"
        if "list" in type_string:
            return "listbox"
        if "sign" in type_string:
            return "signature"
        if code == getattr(fitz, "PDF_WIDGET_TYPE_BUTTON", object()):
            if self._is_push_button(widget):
                return "unknown"
            return "checkbox"
        return "unknown"

    def _is_push_button(self, widget: Any) -> bool:
        try:
            flags = int(getattr(widget, "field_flags", 0) or 0)
        except Exception:
            flags = 0
        return (flags & 65536) != 0

    def _collect_button_states(self, widget: Any) -> list[str]:
        states: list[str] = []
        if hasattr(widget, "button_states"):
            try:
                states.extend(self._flatten_state_values(widget.button_states()))
            except Exception:
                pass
        if hasattr(widget, "on_state"):
            try:
                on_state = widget.on_state()
                if on_state is not None:
                    states.append(str(on_state))
            except Exception:
                pass

        normalized: list[str] = []
        seen: set[str] = set()
        for state in states:
            cleaned = self._normalize_state_name(state)
            if cleaned == "":
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(cleaned)

        if "off" not in {item.lower() for item in normalized}:
            normalized.append("Off")
        return normalized

    def _flatten_state_values(self, raw: Any) -> list[str]:
        if raw is None:
            return []
        if isinstance(raw, dict):
            flat: list[str] = []
            for value in raw.values():
                flat.extend(self._flatten_state_values(value))
            return flat
        if isinstance(raw, (list, tuple, set)):
            flat = []
            for value in raw:
                flat.extend(self._flatten_state_values(value))
            return flat
        return [str(raw)]

    def _normalize_state_name(self, value: Any) -> str:
        text = self._clean_text(str(value))
        if text.startswith("/"):
            text = text[1:]
        return text

    def _flatten_document(self, document: Any):
        if hasattr(document, "bake"):
            document.bake()
            return
        if hasattr(document, "flatten_forms"):
            document.flatten_forms()
            return
        raise NodeException("flatten=True requested, but this PyMuPDF version does not support form flattening")

    def _save_document(self, document: Any, source_path: str, output_path: str):
        if self.overwrite_source:
            temp_path = source_path + ".tmp"
            if os.path.exists(temp_path):
                os.remove(temp_path)
            document.save(temp_path)
            os.replace(temp_path, source_path)
            return

        if os.path.exists(output_path):
            os.remove(output_path)
        document.save(output_path)

    def _normalize_write_value(self, value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        if isinstance(value, (list, tuple)):
            return [self._normalize_write_value(v) for v in value]
        if isinstance(value, dict):
            return {str(k): self._normalize_write_value(v) for k, v in value.items()}
        return str(value)

    def _merge_field_values(self, existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged = dict(existing)
        for key, value in incoming.items():
            merged[str(key)] = value
        return merged

    def _as_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _try_extract_single_path(self, value: Any) -> str | None:
        paths: list[str] = []
        try:
            self._collect_paths(value, paths)
        except Exception:
            return None
        if len(paths) == 0:
            return None
        return paths[0]

    def _dedupe_paths(self, file_paths: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for path in file_paths:
            if path in seen:
                continue
            seen.add(path)
            deduped.append(path)
        return deduped

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text).split())

    def _import_fitz(self):
        try:
            import fitz  # type: ignore

            return fitz
        except Exception as exc:
            raise NodeException(
                "PyMuPDF (fitz) is required for PDFWriteFormAction. Install dependency 'PyMuPDF'."
            ) from exc
