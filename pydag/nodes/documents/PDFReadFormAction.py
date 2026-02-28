from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


def generate_llm_prompt(extracted_fields: list[dict[str, Any]]) -> str:
    """Build a strict bridge prompt for form-filling LLM calls.

    The prompt enforces JSON-only output and key fidelity to PDF field names.
    """
    if len(extracted_fields) == 0:
        return (
            "You are a form-filling assistant. Use the provided RAG context to determine values. "
            "Return ONLY an empty JSON object: {}"
        )

    lines: list[str] = [
        "You are a form-filling assistant. Use the provided RAG context to determine the value for each PDF field.",
        "Return only a strict JSON object mapping each field_name to its determined_value.",
        "Do not add keys, do not remove keys, and do not use markdown.",
        "",
        "Fields:",
    ]

    template: dict[str, str] = {}
    for idx, field_payload in enumerate(extracted_fields, start=1):
        field_name = str(field_payload.get("field_name", "")).strip()
        field_type = str(field_payload.get("field_type", "")).strip()
        tooltip = str(field_payload.get("tooltip", "")).strip()
        visual_label = str(field_payload.get("visual_label", "")).strip()
        page_context = str(field_payload.get("page_context", "")).strip()
        lines.append(
            f'{idx}. field_name="{field_name}" | type="{field_type}" | tooltip="{tooltip}" '
            f'| visual_label="{visual_label}" | page_context="{page_context}"'
        )
        if field_name != "" and field_name not in template:
            template[field_name] = "<determined_value>"

    lines.extend(
        [
            "",
            "Return JSON with exactly these keys and no extras:",
            json.dumps(template, ensure_ascii=True, indent=2),
        ]
    )
    return "\n".join(lines)


@dataclass
class PDFReadFormAction(BufferNode, Action):
    """Extract context-rich AcroForm fields from PDF files using PyMuPDF."""

    input_keys: list[str] = field(default_factory=lambda: ["values"])
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "metadata", "fields", "full_text_content", "llm_prompt"]
    )
    row_mode: str = field(default="per_pdf")
    include_bridge_prompt: bool = field(default=True)
    emit_writable_only: bool = field(default=True)
    require_pdf_extension: bool = field(default=True)
    label_search_left: float = field(default=90.0)
    label_search_above: float = field(default=60.0)
    label_search_right: float = field(default=20.0)
    context_search_padding: float = field(default=140.0)

    def _on_install(self, agent: Agent = None):
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        if len(self.output_keys) != 5:
            raise NodeException(f"{self.cname()} requires exactly 5 output_keys, got {len(self.output_keys)}")
        if self.row_mode not in {"per_pdf", "per_field"}:
            raise NodeException("row_mode must be either 'per_pdf' or 'per_field'")
        for key, value in [
            ("label_search_left", self.label_search_left),
            ("label_search_above", self.label_search_above),
            ("label_search_right", self.label_search_right),
            ("context_search_padding", self.context_search_padding),
        ]:
            if float(value) <= 0:
                raise NodeException(f"{key} must be > 0")

    def _on_execute(self):
        parent_data = self.get_parent_data()
        file_paths = self._extract_paths_from_parent_data(parent_data)
        if len(file_paths) == 0:
            raise NodeException("No PDF file paths were found in parent buffer data")

        for file_path in file_paths:
            self._validate_pdf_path(file_path)
            payload = self._read_pdf(file_path)
            rows = self._build_rows(file_path, payload)
            for row in rows:
                self.add_data({key: [value] for key, value in row.items()})

    def _validate_pdf_path(self, file_path: str):
        if not FileUtils.exists_file(file_path):
            raise NodeException("filepath " + str(file_path) + " does not exist")
        if self.require_pdf_extension and not str(file_path).lower().endswith(".pdf"):
            raise NodeException("filepath " + str(file_path) + " is not a PDF file")

    def _build_rows(self, file_path: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        fields = payload["fields"]
        if self.row_mode == "per_pdf":
            row_fields = [fields]
        elif len(fields) == 0:
            row_fields = [[]]
        else:
            row_fields = [[field_payload] for field_payload in fields]

        rows: list[dict[str, Any]] = []
        for field_row in row_fields:
            prompt = generate_llm_prompt(field_row) if self.include_bridge_prompt else ""
            row = dict(
                zip(
                    self.output_keys,
                    [file_path, payload["metadata"], field_row, payload["full_text_content"], prompt],
                )
            )
            rows.append(row)
        return rows

    def _extract_paths_from_parent_data(self, data: dict[str, Any]) -> list[str]:
        if not data:
            return []
        keys = self.input_keys if len(self.input_keys) > 0 else list(data.keys())
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

    def _read_pdf(self, file_path: str) -> dict[str, Any]:
        fitz = self._import_fitz()
        try:
            document = fitz.open(file_path)
        except Exception as exc:
            raise NodeException("could not read pdf file " + str(file_path)) from exc

        try:
            metadata = self._extract_metadata(document)
            full_text_parts: list[str] = []
            extracted_fields: list[dict[str, Any]] = []

            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                page_text = self._clean_text(page.get_text("text"))
                if page_text != "":
                    full_text_parts.append(page_text)

                words = self._extract_words(page, fitz)
                blocks = self._extract_blocks(page, fitz)
                widgets = page.widgets()
                if widgets is None:
                    continue

                for widget in widgets:
                    field_payload = self._extract_widget_payload(
                        document=document,
                        widget=widget,
                        page_index=page_index,
                        words=words,
                        blocks=blocks,
                        fitz=fitz,
                    )
                    if field_payload is None:
                        continue
                    if self.emit_writable_only and not bool(field_payload.get("is_writable")):
                        continue
                    extracted_fields.append(field_payload)

            return {
                "metadata": metadata,
                "fields": extracted_fields,
                "full_text_content": "\n".join(full_text_parts).strip(),
            }
        finally:
            document.close()

    def _extract_widget_payload(
        self,
        document: Any,
        widget: Any,
        page_index: int,
        words: list[dict[str, Any]],
        blocks: list[dict[str, Any]],
        fitz: Any,
    ) -> dict[str, Any] | None:
        field_name = self._resolve_field_name(document, widget).strip()
        if field_name == "":
            return None

        rect = self._to_rect(widget, fitz)
        if rect is None:
            return None

        tooltip = self._resolve_tooltip(document, widget)
        field_type = self._classify_widget_type(widget, fitz)
        is_writable = self._is_writable_widget(widget, field_type)
        button_states = self._collect_button_states(widget)
        visual_label = self._infer_visual_label(rect, words, fitz)
        if visual_label == "" and tooltip != "":
            visual_label = tooltip
        page_context = self._infer_page_context(rect, blocks, fitz)
        field_value = self._normalize_field_value(getattr(widget, "field_value", None))

        return {
            "field_name": field_name,
            "field_type": field_type,
            "field_value": field_value,
            "tooltip": tooltip,
            "visual_label": visual_label,
            "page_context": page_context,
            "page_index": int(page_index),
            "rect": [float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)],
            "is_writable": bool(is_writable),
            "button_states": button_states,
        }

    def _extract_metadata(self, document: Any) -> dict[str, Any]:
        metadata: dict[str, Any] = {"pages": int(document.page_count)}
        raw = getattr(document, "metadata", None)
        if isinstance(raw, dict):
            for key, value in raw.items():
                if value is None:
                    continue
                cleaned = self._clean_text(str(value))
                if cleaned == "":
                    continue
                metadata[str(key)] = cleaned
        return metadata

    def _extract_words(self, page: Any, fitz: Any) -> list[dict[str, Any]]:
        words_raw = page.get_text("words") or []
        words: list[dict[str, Any]] = []
        for row in words_raw:
            if len(row) < 5:
                continue
            text = self._clean_text(str(row[4]))
            if text == "":
                continue
            rect = fitz.Rect(float(row[0]), float(row[1]), float(row[2]), float(row[3]))
            words.append({"text": text, "rect": rect})
        return words

    def _extract_blocks(self, page: Any, fitz: Any) -> list[dict[str, Any]]:
        blocks_raw = page.get_text("blocks") or []
        blocks: list[dict[str, Any]] = []
        for row in blocks_raw:
            if len(row) < 5:
                continue
            text = self._clean_text(str(row[4]))
            if text == "":
                continue
            rect = fitz.Rect(float(row[0]), float(row[1]), float(row[2]), float(row[3]))
            blocks.append({"text": text, "rect": rect})
        return blocks

    def _resolve_field_name(self, document: Any, widget: Any) -> str:
        direct = self._clean_text(str(getattr(widget, "field_name", "") or ""))
        if direct != "":
            return direct
        return self._read_widget_pdf_key(document, widget, "T")

    def _resolve_tooltip(self, document: Any, widget: Any) -> str:
        label = self._clean_text(str(getattr(widget, "field_label", "") or ""))
        if label != "":
            return label
        return self._read_widget_pdf_key(document, widget, "TU")

    def _read_widget_pdf_key(self, document: Any, widget: Any, key: str) -> str:
        xref = getattr(widget, "xref", 0)
        if not isinstance(xref, int) or xref <= 0:
            return ""
        try:
            _, raw_value = document.xref_get_key(xref, key)
        except Exception:
            return ""
        if raw_value is None:
            return ""
        text = str(raw_value).strip()
        if text.startswith("(") and text.endswith(")") and len(text) >= 2:
            text = text[1:-1]
        return self._clean_text(text)

    def _to_rect(self, widget: Any, fitz: Any) -> Any | None:
        rect = getattr(widget, "rect", None)
        if rect is None:
            return None
        try:
            return fitz.Rect(rect)
        except Exception:
            return None

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

    def _is_writable_widget(self, widget: Any, field_type: str) -> bool:
        if field_type in {"text", "checkbox", "radio", "dropdown", "listbox"}:
            if field_type in {"checkbox", "radio"} and self._is_push_button(widget):
                return False
            return True
        return False

    def _collect_button_states(self, widget: Any) -> list[str]:
        states: list[str] = []

        if hasattr(widget, "button_states"):
            try:
                raw_states = widget.button_states()
                states.extend(self._flatten_state_values(raw_states))
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
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
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

    def _normalize_field_value(self, value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            text = str(value)
            if text.startswith("/"):
                return text[1:]
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        return self._clean_text(str(value))

    def _infer_visual_label(self, field_rect: Any, words: list[dict[str, Any]], fitz: Any) -> str:
        search_rect = fitz.Rect(
            field_rect.x0 - float(self.label_search_left),
            field_rect.y0 - float(self.label_search_above),
            field_rect.x1 + float(self.label_search_right),
            field_rect.y1 + 8.0,
        )

        candidates: list[dict[str, Any]] = []
        target_y = (field_rect.y0 + field_rect.y1) / 2.0
        for word in words:
            word_rect = word["rect"]
            if not search_rect.intersects(word_rect):
                continue
            center_x = (word_rect.x0 + word_rect.x1) / 2.0
            center_y = (word_rect.y0 + word_rect.y1) / 2.0
            y_delta = abs(center_y - target_y)
            x_penalty = 0.0 if center_x <= field_rect.x0 else abs(center_x - field_rect.x0) + 60.0
            score = y_delta * 3.0 + x_penalty
            candidates.append({"text": word["text"], "rect": word_rect, "score": score})

        if len(candidates) == 0:
            return ""

        candidates.sort(key=lambda item: float(item["score"]))
        anchor = candidates[0]
        anchor_rect = anchor["rect"]
        line_words = [
            item
            for item in candidates
            if abs(((item["rect"].y0 + item["rect"].y1) / 2.0) - ((anchor_rect.y0 + anchor_rect.y1) / 2.0)) <= 4.5
        ]
        line_words.sort(key=lambda item: float(item["rect"].x0))
        return self._clean_text(" ".join([item["text"] for item in line_words]))

    def _infer_page_context(self, field_rect: Any, blocks: list[dict[str, Any]], fitz: Any) -> str:
        padding = float(self.context_search_padding)
        context_rect = fitz.Rect(
            field_rect.x0 - padding,
            field_rect.y0 - padding,
            field_rect.x1 + padding,
            field_rect.y1 + padding,
        )

        above_candidates: list[dict[str, Any]] = []
        near_candidates: list[dict[str, Any]] = []
        for block in blocks:
            block_rect = block["rect"]
            if block_rect.y1 <= field_rect.y0 + 2.0:
                overlap = min(block_rect.x1, field_rect.x1 + padding) - max(block_rect.x0, field_rect.x0 - padding)
                if overlap >= -2.0:
                    distance = field_rect.y0 - block_rect.y1
                    above_candidates.append({"text": block["text"], "distance": distance})
            if context_rect.intersects(block_rect):
                center_x = (block_rect.x0 + block_rect.x1) / 2.0
                center_y = (block_rect.y0 + block_rect.y1) / 2.0
                field_center_x = (field_rect.x0 + field_rect.x1) / 2.0
                field_center_y = (field_rect.y0 + field_rect.y1) / 2.0
                distance = abs(center_x - field_center_x) + abs(center_y - field_center_y)
                near_candidates.append({"text": block["text"], "distance": distance})

        if len(above_candidates) > 0:
            above_candidates.sort(key=lambda item: float(item["distance"]))
            return self._truncate_context(above_candidates[0]["text"])
        if len(near_candidates) > 0:
            near_candidates.sort(key=lambda item: float(item["distance"]))
            return self._truncate_context(near_candidates[0]["text"])
        return ""

    def _truncate_context(self, text: str, max_len: int = 220) -> str:
        clean = self._clean_text(text)
        if len(clean) <= max_len:
            return clean
        return clean[:max_len].rstrip() + "..."

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text).split())

    def _import_fitz(self):
        try:
            import fitz  # type: ignore

            return fitz
        except Exception as exc:
            raise NodeException(
                "PyMuPDF (fitz) is required for PDFReadFormAction. Install dependency 'PyMuPDF'."
            ) from exc
