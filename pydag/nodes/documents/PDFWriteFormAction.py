from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
from typing import Any

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ...utils.PDFUtils import PDFUtils as _pdf_utils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class PDFWriteFormAction(BufferNode, Action):
    """Write LLM- or user-provided values into PDF AcroForm fields using PyMuPDF."""

    BUTTON_FIELD_TYPES = {"checkbox", "radio"}
    TEXT_FIELD_TYPES = {"text", "dropdown", "listbox"}
    WRITABLE_FIELD_TYPES = BUTTON_FIELD_TYPES | TEXT_FIELD_TYPES
    PATH_MAPPING_KEYS = ("filepath", "file_path", "pdf_path", "pdf")
    PAYLOAD_WRAPPER_KEYS = ("answer", "answers", "values", "data", "content", "llm_data", "fields", "field_values")
    TRUTHY_BUTTON_VALUES = {"1", "true", "yes", "on", "x", "checked", "selected", "ja", "y"}
    FALSY_BUTTON_VALUES = {"0", "false", "no", "off", "unchecked", "none", "", "nein", "n"}

    path_input_keys: list[str] = field(
        default_factory=lambda: ["values", "filepath", "pdf_path"],
        metadata={"description": "parent buffer keys to scan for source PDF file paths"},
    )
    fill_input_keys: list[str] = field(
        default_factory=lambda: ["answer", "answers", "fields", "field_values", "llm_data", "content"],
        metadata={"description": "parent buffer keys to scan for strict field_updates payloads whose field values are the final PDF write instructions: each update uses internal_field_id plus either value for text/dropdown/list fields or selected_state for checkbox/radio fields"},
    )
    row_mode: str = field(
        default="per_pdf",
        metadata={"description": "payload interpretation mode: per_pdf expects one payload per file, per_field can merge field-level rows"},
    )
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "output_filepath", "written_fields", "written_field_count"],
        metadata={"description": "output columns for source path, written file path, field map, and number of written fields"},
    )
    output_folder: str | None = field(
        default="resources/outputs",
        metadata={"description": "target folder for written PDFs; ignored when overwrite_source is True"},
    )
    output_suffix: str = field(
        default="_filled",
        metadata={"description": "suffix appended to the source filename stem for generated output files"},
    )
    overwrite_source: bool = field(
        default=False,
        metadata={"description": "whether to overwrite the source PDF in place instead of writing a separate output file"},
    )
    flatten: bool = field(
        default=False,
        metadata={"description": "whether to flatten form fields after writing values"},
    )
    strict_unknown_fields: bool = field(
        default=True,
        metadata={"description": "whether to raise an error if payload contains field names that are not present in the PDF"},
    )
    require_pdf_extension: bool = field(
        default=True,
        metadata={"description": "whether file paths must end with .pdf"},
    )

    def _on_install(self, agent: Agent = None):
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        BufferNode._validate_keys(self.path_input_keys)
        BufferNode._validate_keys(self.fill_input_keys)
        if len(self.output_keys) != 4:
            raise NodeException(f"{self.cname()} requires exactly 4 output_keys, got {len(self.output_keys)}")
        if self.row_mode not in {"per_pdf", "per_field"}:
            raise NodeException("row_mode must be either 'per_pdf' or 'per_field'")
        if self.overwrite_source and self.output_folder is not None:
            raise NodeException("output_folder cannot be set when overwrite_source=True")

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

    def _wrapped_payload_values(self, payload: dict[str, Any]):
        for key in self.PAYLOAD_WRAPPER_KEYS:
            if key in payload:
                yield payload[key]

    def _merge_payloads(self, payloads: list[dict[str, Any]]) -> dict[str, Any] | None:
        merged: dict[str, Any] = {}
        for payload in payloads:
            merged = self._merge_field_values(merged, payload)
        return merged if len(merged) > 0 else None

    def _extract_payloads_by_path(self, data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        mapping: dict[str, dict[str, Any]] = {}
        present_path_keys = [key for key in self.PATH_MAPPING_KEYS if key in data]
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
        return [
            normalized
            for candidate in candidates
            for normalized in [self._normalize_payload(candidate)]
            if normalized is not None and len(normalized) > 0
        ]

    def _collect_payload_candidates(self, value: Any, target: list[Any]):
        if value is None:
            return
        if isinstance(value, str):
            target.append(value)
            return
        if isinstance(value, dict):
            if "field_updates" in value or self._looks_like_update_item(value):
                target.append(value)
                return
            for wrapped_value in self._wrapped_payload_values(value):
                self._collect_payload_candidates(wrapped_value, target)
            return
        if isinstance(value, (list, tuple)):
            if self._looks_like_update_list(value):
                target.append(list(value))
                return
            for item in value:
                self._collect_payload_candidates(item, target)
            return
        target.append(value)

    def _looks_like_update_list(self, value: Any) -> bool:
        if not isinstance(value, (list, tuple)) or len(value) == 0:
            return False
        if not all(isinstance(item, dict) for item in value):
            return False
        return all(self._looks_like_update_item(item) for item in value)

    def _looks_like_update_item(self, payload: dict[str, Any]) -> bool:
        has_field = "internal_field_id" in payload and str(payload.get("internal_field_id", "")).strip() != ""
        has_value = any(key in payload for key in ("selected_state", "value"))
        return has_field and has_value

    def _normalize_payload(self, payload: Any) -> dict[str, Any] | None:
        if payload is None:
            return None

        if isinstance(payload, str):
            parsed = self._parse_payload_text(payload)
            return self._normalize_payload(parsed)

        if isinstance(payload, (list, tuple)):
            if self._looks_like_update_list(payload):
                return self._normalize_update_list(payload)
            normalized_items = [
                normalized
                for item in payload
                for normalized in [self._normalize_payload(item)]
                if normalized is not None and len(normalized) > 0
            ]
            return self._merge_payloads(normalized_items)

        if isinstance(payload, dict):
            if "field_updates" in payload:
                return self._normalize_payload(payload["field_updates"])

            if self._looks_like_update_item(payload):
                return self._normalize_update_item(payload)

            for wrapped_value in self._wrapped_payload_values(payload):
                normalized = self._normalize_payload(wrapped_value)
                if normalized is not None and len(normalized) > 0:
                    return normalized
            raise NodeException(
                "Invalid fill payload object. Expected field_updates list or update item with internal_field_id."
            )

        return None

    def _normalize_update_list(self, payload: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any] | None:
        normalized_items = [
            normalized
            for item in payload
            if isinstance(item, dict)
            for normalized in [self._normalize_update_item(item)]
            if normalized is not None
        ]
        return self._merge_payloads(normalized_items)

    def _normalize_update_item(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        target = str(payload.get("internal_field_id", "")).strip()
        if target == "":
            raise NodeException("Each field update requires internal_field_id")

        has_selected_state = "selected_state" in payload
        has_value = "value" in payload
        if has_selected_state and has_value:
            raise NodeException("Field update for " + target + " must contain only one of selected_state or value")
        if not has_selected_state and not has_value:
            raise NodeException("Field update for " + target + " must contain selected_state or value")
        raw_value = payload.get("selected_state") if has_selected_state else payload.get("value")
        normalized_value = self._normalize_write_value(raw_value)
        if has_value:
            normalized_value = self._normalize_text_update_value(normalized_value)
        return {target: normalized_value}

    def _json_payload_candidates(self, text: str) -> list[str]:
        candidates = [text]
        for start_char, end_char in (("{", "}"), ("[", "]")):
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start >= 0 and end > start:
                candidate = text[start : end + 1]
                if candidate not in candidates:
                    candidates.append(candidate)
        return candidates

    def _parse_payload_text(self, text: str) -> Any:
        clean = str(text).strip()
        if clean == "":
            raise NodeException("Fill payload text is empty")

        if clean.startswith("```"):
            lines = clean.splitlines()
            if len(lines) >= 2:
                lines = lines[1:]
                if len(lines) > 0 and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                clean = "\n".join(lines).strip()

        for candidate in self._json_payload_candidates(clean):
            try:
                return json.loads(candidate)
            except Exception:
                continue
        raise NodeException(
            "Could not parse fill payload as JSON for strict field_updates contract"
        )

    def _normalize_sequential_payloads(
        self,
        sequential_payloads: list[dict[str, Any]],
        file_paths: list[str],
        has_payloads_by_path: bool,
    ) -> list[dict[str, Any]]:
        if self.row_mode == "per_pdf" or has_payloads_by_path:
            return sequential_payloads
        if len(sequential_payloads) == 0:
            return []

        if len(file_paths) == 1:
            merged = self._merge_payloads(sequential_payloads)
            return [merged] if merged is not None else []

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
        output_path = str(folder / output_name)
        if os.path.normcase(os.path.abspath(output_path)) == os.path.normcase(os.path.abspath(source_path)):
            raise NodeException(
                "output path resolves to the source PDF; set overwrite_source=True or change output_folder/output_suffix"
            )
        return output_path

    def _resolve_writable_field_values(
        self,
        field_values: dict[str, Any],
        widgets_by_field: dict[str, list[Any]],
        canonical_lookup: dict[str, list[str]],
    ) -> tuple[dict[str, Any], list[str]]:
        writable_values: dict[str, Any] = {}
        unknown_fields: list[str] = []
        for source_name, value in field_values.items():
            resolved_name = self._resolve_known_field_name(
                source_name,
                widgets_by_field=widgets_by_field,
                canonical_lookup=canonical_lookup,
            )
            if resolved_name is None:
                unknown_fields.append(str(source_name))
                continue
            writable_values[resolved_name] = value
        return writable_values, unknown_fields

    def _write_pdf(self, source_path: str, output_path: str, field_values: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(field_values, dict):
            raise NodeException("field_values must be a mapping of PDF field names to values")
        fitz = _pdf_utils.import_fitz()
        try:
            document = fitz.open(source_path)
        except Exception as exc:
            raise NodeException("could not read pdf file " + str(source_path)) from exc

        try:
            widgets_by_field, _page_refs = self._index_widgets(document)
            canonical_lookup = self._build_canonical_field_lookup(list(widgets_by_field.keys()))
            writable_values, unknown_fields = self._resolve_writable_field_values(
                field_values,
                widgets_by_field=widgets_by_field,
                canonical_lookup=canonical_lookup,
            )
            if self.strict_unknown_fields and len(unknown_fields) > 0:
                raise NodeException(
                    "unknown PDF field(s): " + ", ".join(sorted(unknown_fields))
                )

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
            try:
                document.close()
            except Exception:
                pass

    def _index_widgets(self, document: Any) -> tuple[dict[str, list[Any]], list[Any]]:
        widgets_by_field: dict[str, list[Any]] = {}
        page_refs: list[Any] = []
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            page_refs.append(page)
            widgets = page.widgets()
            if widgets is None:
                continue
            for widget in widgets:
                field_name = _pdf_utils.clean_text(str(getattr(widget, "field_name", "") or ""))
                if field_name == "":
                    continue
                widgets_by_field.setdefault(field_name, []).append(widget)
        return widgets_by_field, page_refs

    def _write_field_to_widgets(self, field_name: str, widgets: list[Any], value: Any, fitz: Any) -> Any:
        if len(widgets) == 0:
            raise NodeException("No widgets found for field " + str(field_name))

        widget_types = [_pdf_utils.classify_widget_type(widget, fitz) for widget in widgets]
        writable_types = [kind for kind in widget_types if kind in self.WRITABLE_FIELD_TYPES]
        if len(writable_types) == 0:
            raise NodeException("Field " + str(field_name) + " is not writable")

        if all(kind in self.BUTTON_FIELD_TYPES for kind in writable_types):
            return self._write_button_group(widgets, value)

        if any(kind in self.BUTTON_FIELD_TYPES for kind in writable_types):
            raise NodeException("Mixed button/text widget group is unsupported for field " + str(field_name))

        text_value = self._to_text_field_value(value)
        first_written_widget: Any | None = None
        for widget, kind in zip(widgets, widget_types):
            if kind not in self.TEXT_FIELD_TYPES:
                continue
            widget.field_value = text_value
            widget.update()
            if first_written_widget is None:
                first_written_widget = widget

        if first_written_widget is None:
            return text_value

        persisted_value = getattr(first_written_widget, "field_value", text_value)
        return self._normalize_write_value(persisted_value)

    def _write_button_group(self, widgets: list[Any], value: Any) -> str:
        union_states = self._collect_group_states(widgets)
        target_state = self._resolve_target_button_state(value, union_states)
        target_token = self._normalize_state_token(target_state)

        for widget in widgets:
            widget_states = _pdf_utils.collect_button_states(widget)
            lookup = {self._normalize_state_token(state): state for state in widget_states}
            off_state = self._resolve_off_state(widget_states)
            write_state = lookup.get(target_token, off_state)
            widget.field_value = write_state
            widget.update()
        return target_state

    def _collect_group_states(self, widgets: list[Any]) -> list[str]:
        states: list[str] = []
        seen: set[str] = set()
        for widget in widgets:
            for state in _pdf_utils.collect_button_states(widget):
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

        state_lookup = {_pdf_utils.clean_text(str(state)).lower(): state for state in available_states}
        normalized_lookup: dict[str, str] = {}
        for state in available_states:
            token = self._normalize_state_token(state)
            if token == "" or token in normalized_lookup:
                continue
            normalized_lookup[token] = state

        off_state = self._resolve_off_state(available_states)
        on_candidates = [state for state in available_states if state.lower() != off_state.lower()]
        available_text = ", ".join(available_states)

        raw_clean = "" if value is None else _pdf_utils.clean_text(str(value))
        raw_lower = raw_clean.lower()
        if raw_lower in state_lookup:
            return state_lookup[raw_lower]

        normalized_value = self._normalize_state_token(value)
        if normalized_value != "" and normalized_value in normalized_lookup:
            return normalized_lookup[normalized_value]

        semantic_value: bool | None = None
        if isinstance(value, bool):
            semantic_value = value
        elif isinstance(value, (int, float)):
            semantic_value = float(value) != 0.0
        elif value is None:
            semantic_value = False
        elif normalized_value in self.TRUTHY_BUTTON_VALUES:
            semantic_value = True
        elif normalized_value in self.FALSY_BUTTON_VALUES:
            semantic_value = False

        if semantic_value is not None:
            return self._resolve_semantic_button_state(
                semantic_value=semantic_value,
                on_candidates=on_candidates,
                off_state=off_state,
                raw_value=value,
                available_text=available_text,
            )

        # Controlled fallback: only choose ON automatically for effectively binary groups.
        if len(on_candidates) == 1:
            return on_candidates[0]

        raise NodeException(
            "Could not map button value '"
            + str(value)
            + "' to available states: "
            + available_text
        )

    def _resolve_semantic_button_state(
        self,
        semantic_value: bool,
        on_candidates: list[str],
        off_state: str,
        raw_value: Any,
        available_text: str,
    ) -> str:
        if semantic_value is False:
            return off_state
        if len(on_candidates) == 1:
            return on_candidates[0]
        raise NodeException(
            "Ambiguous ON-state for button value '"
            + str(raw_value)
            + "'. Available states: "
            + available_text
        )

    def _resolve_off_state(self, states: list[str]) -> str:
        return next((state for state in states if state.lower() == "off"), "Off")

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

    def _normalize_state_token(self, value: Any) -> str:
        if value is None:
            return ""
        return _pdf_utils.clean_text(_pdf_utils.normalize_state_name(value)).lower()

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

    def _normalize_text_update_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        text = _pdf_utils.clean_text(value)
        if ":" in text:
            prefix, suffix = text.split(":", 1)
            suffix = _pdf_utils.clean_text(suffix)
            if suffix != "" and self._looks_like_structured_identifier(suffix):
                text = suffix
            elif suffix != "" and len(prefix.split()) <= 4 and re.search(r"\d", suffix):
                text = suffix
        if self._looks_like_spaced_identifier(text):
            return self._collapse_spaced_identifier(text)
        return text

    def _looks_like_structured_identifier(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        if clean == "":
            return False
        if re.search(r"[A-Z0-9]{6,}", clean.replace(" ", "")):
            return True
        if re.search(r"\d", clean):
            return True
        return False

    def _looks_like_spaced_identifier(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        tokens = clean.split()
        if len(tokens) < 6:
            return False
        compact = "".join(ch for ch in clean if ch.isalnum())
        if len(compact) < 8:
            return False
        return all(token.isalnum() and len(token) == 1 for token in tokens)

    def _collapse_spaced_identifier(self, text: str) -> str:
        return "".join(ch for ch in str(text) if ch.isalnum())

    def _merge_field_values(self, existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged = dict(existing)
        for key, value in incoming.items():
            merged[str(key)] = value
        return merged

    def _as_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        return value if isinstance(value, list) else list(value) if isinstance(value, tuple) else [value]

    def _try_extract_single_path(self, value: Any) -> str | None:
        paths: list[str] = []
        try:
            self._collect_paths(value, paths)
        except Exception:
            return None
        return paths[0] if len(paths) > 0 else None

    def _dedupe_paths(self, file_paths: list[str]) -> list[str]:
        return list(dict.fromkeys(file_paths))

    def _build_canonical_field_lookup(self, field_names: list[str]) -> dict[str, list[str]]:
        lookup: dict[str, list[str]] = {}
        for name in field_names:
            token = _pdf_utils.canonicalize_field_key(name)
            if token == "":
                continue
            lookup.setdefault(token, []).append(name)
        return lookup

    def _resolve_known_field_name(
        self,
        source_name: Any,
        widgets_by_field: dict[str, list[Any]],
        canonical_lookup: dict[str, list[str]],
    ) -> str | None:
        cleaned = _pdf_utils.clean_text(str(source_name))
        if cleaned in widgets_by_field:
            return cleaned

        token = _pdf_utils.canonicalize_field_key(cleaned)
        if token == "":
            return None
        candidates = canonical_lookup.get(token, [])
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise NodeException(
                "Ambiguous internal_field_id '" + cleaned + "' matches: " + ", ".join(sorted(candidates))
            )
        return None
