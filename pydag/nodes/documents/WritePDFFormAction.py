import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class WritePDFFormAction(BufferNode, Action):
    """`Action` that writes form values into parent-provided PDF files."""

    path_input_keys: list[str] = field(
        default_factory=lambda: ["values", "filepath"],
        metadata={"description": "keys used to extract source PDF paths from parent data"},
    )
    fill_input_keys: list[str] = field(
        default_factory=lambda: ["answer", "answers", "fields", "form_fields", "field_values", "content"],
        metadata={"description": "keys used to extract filled form payloads from parent data"},
    )
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "output_filepath", "written_fields", "written_field_count"],
        metadata={
            "description": "output keys in the order [filepath, output_filepath, written_fields, written_field_count]"
        },
    )
    output_suffix: str = field(
        default="_filled",
        metadata={"description": "suffix appended to output files when overwrite_source is False"},
    )
    output_folder: str = field(
        default=None,
        metadata={"description": "optional folder for written PDFs; defaults to source file folder"},
    )
    overwrite_source: bool = field(
        default=False,
        metadata={"description": "if True, write directly into source PDFs"},
    )
    require_pdf_extension: bool = field(
        default=True,
        metadata={"description": "if True, reject non-.pdf inputs before parsing"},
    )
    require_two_parents: bool = field(
        default=True,
        metadata={"description": "if True, require at least two parents (paths + fill payloads)"},
    )

    def _on_install(self, agent: Agent = None):
        """Install and validate output schema requirements."""
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        if len(self.output_keys) != 4:
            raise NodeException(
                f"{self.cname()} requires exactly 4 output_keys, got {len(self.output_keys)}"
            )
        if self.overwrite_source and self.output_folder is not None:
            raise NodeException("output_folder cannot be used when overwrite_source=True")

    def _on_execute(self):
        """Extract file paths + fill payloads from parents and write one output PDF per input path."""
        if self.require_two_parents and len(self.get_parents()) < 2:
            raise NodeException(
                f"{self.cname()} requires at least two parents: one for file paths and one for filled form values"
            )

        data = self.get_parent_data()
        if not data:
            raise NodeException("No parent data was found")

        file_paths = self._extract_paths_from_parent_data(data)
        if len(file_paths) == 0:
            raise NodeException("No PDF file paths were found in parent buffer data")

        payloads_by_path = self._extract_payloads_by_path(data)
        if len(payloads_by_path) > 0:
            file_paths = self._dedupe_paths(file_paths)
        sequential_payloads = self._extract_fill_payloads(data)
        if len(payloads_by_path) == 0 and len(sequential_payloads) == 0:
            raise NodeException("No valid filled form payloads were found in parent buffer data")

        if len(payloads_by_path) == 0 and len(sequential_payloads) not in (0, 1, len(file_paths)):
            raise NodeException(
                f"number of filled payloads ({len(sequential_payloads)}) must be 1 or equal to number of paths ({len(file_paths)})"
            )

        for idx, file_path in enumerate(file_paths):
            self._validate_file_path(file_path)

            field_values = payloads_by_path.get(file_path)
            if field_values is None:
                if len(sequential_payloads) == 1:
                    field_values = sequential_payloads[0]
                elif len(sequential_payloads) == len(file_paths):
                    field_values = sequential_payloads[idx]
                else:
                    raise NodeException("No matching filled payload for filepath " + file_path)

            output_path = self._resolve_output_path(file_path)
            written_field_count = self._write_pdf(file_path, output_path, field_values)

            row = dict(
                zip(
                    self.output_keys,
                    [file_path, output_path, field_values, written_field_count],
                )
            )
            self.add_data({key: [value] for key, value in row.items()})

    def _validate_file_path(self, file_path: str):
        """Fail fast for missing or invalid source paths."""
        if not FileUtils.exists_file(file_path):
            raise NodeException("filepath " + file_path + " does not exist")
        if self.require_pdf_extension and not file_path.lower().endswith(".pdf"):
            raise NodeException("filepath " + file_path + " is not a PDF file")

    def _extract_paths_from_parent_data(self, data: dict) -> list[str]:
        """Select configured path keys and flatten their values into a list of file paths."""
        keys = self.path_input_keys if len(self.path_input_keys) > 0 else ["values"]
        paths: list[str] = []
        for key in keys:
            if key in data:
                self._collect_paths(data[key], paths)
        return paths

    def _collect_paths(self, value: Any, target: list[str]):
        """Recursively flatten nested path iterables and validate each path string."""
        if isinstance(value, str):
            path = value.strip()
            if path == "":
                raise NodeException("empty file path in parent data")
            target.append(path)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect_paths(item, target)
        else:
            raise NodeException("unsupported parent data type for file path extraction: " + str(type(value)))

    def _extract_fill_payloads(self, data: dict) -> list[dict[str, Any]]:
        """Extract sequential payloads from configured fill keys."""
        payload_candidates: list[Any] = []
        keys = self.fill_input_keys if len(self.fill_input_keys) > 0 else list(data.keys())
        for key in keys:
            if key in data:
                self._collect_payload_candidates(data[key], payload_candidates)

        payloads: list[dict[str, Any]] = []
        for candidate in payload_candidates:
            normalized = self._normalize_field_values(candidate)
            if normalized is not None and len(normalized) > 0:
                payloads.append(normalized)
        return payloads

    def _extract_payloads_by_path(self, data: dict) -> dict[str, dict[str, Any]]:
        """Extract filepath->payload mappings when both filepath and fill columns are present."""
        mapping: dict[str, dict[str, Any]] = {}
        path_keys = ["filepath", "file_path", "pdf_path", "pdf"]
        present_path_keys = [k for k in path_keys if k in data]
        present_fill_keys = [k for k in self.fill_input_keys if k in data]

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
                    file_path = self._try_extract_single_path(path_values[idx])
                    if file_path is None:
                        continue
                    normalized = self._normalize_field_values(fill_values[idx])
                    if normalized is not None and len(normalized) > 0:
                        existing = mapping.get(file_path)
                        if existing is None:
                            mapping[file_path] = normalized
                        else:
                            mapping[file_path] = self._merge_field_values(existing, normalized)
        return mapping

    def _collect_payload_candidates(self, value: Any, target: list[Any]):
        """Flatten payload containers while preserving row-level field lists."""
        if value is None:
            return
        if isinstance(value, (str, dict)):
            target.append(value)
            return
        if isinstance(value, (list, tuple)):
            if self._looks_like_field_list(value):
                target.append(list(value))
            else:
                for item in value:
                    self._collect_payload_candidates(item, target)
            return
        target.append(value)

    def _looks_like_field_list(self, value: Any) -> bool:
        """Return True for a list of field dictionaries using read-action style schema."""
        return (
            isinstance(value, (list, tuple))
            and len(value) > 0
            and all(isinstance(item, dict) for item in value)
            and any("field_id" in item for item in value)
        )

    def _normalize_field_values(self, payload: Any) -> dict[str, Any] | None:
        """Normalize supported payload formats into {field_id: value}."""
        if payload is None:
            return None

        if isinstance(payload, str):
            parsed = self._parse_payload_text(payload)
            if parsed is None:
                return None
            return self._normalize_field_values(parsed)

        if isinstance(payload, (list, tuple)):
            if self._looks_like_field_list(payload):
                result = {}
                for item in payload:
                    field_id = item.get("field_id")
                    if field_id is None:
                        continue
                    value = self._coalesce(
                        item.get("current_value"),
                        item.get("value"),
                        item.get("field_value"),
                        item.get("answer"),
                        "",
                    )
                    if self._is_empty_value(value):
                        continue
                    result[str(field_id)] = self._normalize_write_value(value)
                return result if len(result) > 0 else None
            if len(payload) == 1:
                return self._normalize_field_values(payload[0])
            return None

        if isinstance(payload, dict):
            for wrapper_key in ["fields", "form_fields", "field_values", "values", "answer", "content", "data"]:
                if wrapper_key in payload:
                    nested = self._normalize_field_values(payload[wrapper_key])
                    if nested is not None and len(nested) > 0:
                        return nested

            if "field_id" in payload:
                field_id = payload.get("field_id")
                if field_id is None:
                    return None
                value = self._coalesce(
                    payload.get("current_value"),
                    payload.get("value"),
                    payload.get("field_value"),
                    payload.get("answer"),
                    "",
                )
                if self._is_empty_value(value):
                    return None
                return {str(field_id): self._normalize_write_value(value)}

            result = {}
            for key, value in payload.items():
                if key in {"filepath", "file_path", "metadata", "full_text_content", "question", "prompt"}:
                    continue
                if isinstance(value, (dict, list, tuple)):
                    nested = self._normalize_field_values(value)
                    if nested is not None and len(nested) > 0:
                        result.update(nested)
                        continue
                if self._is_empty_value(value):
                    continue
                result[str(key)] = self._normalize_write_value(value)
            return result if len(result) > 0 else None

        return None

    def _parse_payload_text(self, text: str) -> Any:
        """Best-effort JSON parsing for plain JSON and fenced markdown JSON answers."""
        clean = text.strip()
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

    def _resolve_output_path(self, source_path: str) -> str:
        """Build output path based on overwrite/source folder/suffix settings."""
        if self.overwrite_source:
            return source_path

        src = Path(source_path)
        target_folder = Path(self.output_folder) if self.output_folder is not None else src.parent
        target_name = src.stem + self.output_suffix + src.suffix
        output_path = target_folder / target_name
        return str(output_path)

    def _write_pdf(self, source_path: str, output_path: str, field_values: dict[str, Any]) -> int:
        """Write normalized field values to a target PDF path."""
        try:
            reader = PdfReader(source_path)
        except Exception as e:
            raise NodeException("could not read pdf file " + source_path) from e

        try:
            # Guard against synthetic/non-form keys and keep output aligned with actual writable fields.
            available_field_names = set((reader.get_fields() or {}).keys())
            if len(available_field_names) > 0:
                filtered_field_values = {k: v for k, v in field_values.items() if k in available_field_names}
            else:
                filtered_field_values = dict(field_values)
            field_values.clear()
            field_values.update(filtered_field_values)

            writer = PdfWriter()
            writer.clone_document_from_reader(reader)
            for page in writer.pages:
                writer.update_page_form_field_values(page, field_values, auto_regenerate=False)

            acroform = writer._root_object.get("/AcroForm")
            if acroform is not None:
                acroform_obj = acroform.get_object() if hasattr(acroform, "get_object") else acroform
                if hasattr(acroform_obj, "update"):
                    acroform_obj.update({NameObject("/NeedAppearances"): BooleanObject(True)})

            target_folder = FileUtils.parent_folder(output_path)
            if target_folder:
                FileUtils.create_dir(target_folder)

            with open(output_path, "wb") as stream:
                writer.write(stream)
        except Exception as e:
            raise NodeException("could not write pdf file " + output_path) from e

        return len(field_values)

    def _as_list(self, value: Any) -> list[Any]:
        """Wrap scalars as a list while preserving existing list/tuple values."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _try_extract_single_path(self, value: Any) -> str | None:
        """Best-effort extraction of one path from a value without raising errors."""
        paths = []
        try:
            self._collect_paths(value, paths)
        except Exception:
            return None
        if len(paths) == 0:
            return None
        return paths[0]

    def _normalize_write_value(self, value: Any) -> Any:
        """Normalize output field values to primitive/serializable forms."""
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
        """Merge two field maps using last-non-empty-wins semantics."""
        merged = dict(existing)
        for key, value in incoming.items():
            if key not in merged:
                merged[key] = value
                continue
            if not self._is_empty_value(value):
                merged[key] = value
        return merged

    def _is_empty_value(self, value: Any) -> bool:
        """Return True for None or blank string values used in merge decisions."""
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ""
        return False

    def _dedupe_paths(self, file_paths: list[str]) -> list[str]:
        """Preserve order while deduplicating identical source PDF paths."""
        seen = set()
        deduped = []
        for path in file_paths:
            if path in seen:
                continue
            seen.add(path)
            deduped.append(path)
        return deduped

    def _coalesce(self, *values: Any) -> Any:
        """Return first non-empty value (ignores None and blank strings)."""
        for value in values:
            if value is None:
                continue
            if isinstance(value, str):
                if value.strip() == "":
                    continue
                return value
            return value
        return None
