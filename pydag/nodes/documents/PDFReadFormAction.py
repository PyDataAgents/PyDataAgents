from __future__ import annotations

from dataclasses import dataclass, field
import json
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
class PDFReadFormAction(BufferNode, Action):
    """Extract context-rich AcroForm fields from PDF files using PyMuPDF."""

    BUTTON_FIELD_TYPES = {"checkbox", "radio"}
    WRITABLE_FIELD_TYPES = {"text", "checkbox", "radio", "dropdown", "listbox"}

    input_keys: list[str] = field(
        default_factory=lambda: ["values"],
        metadata={"description": "parent buffer keys to scan for PDF file paths"},
    )
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "metadata", "fields", "full_text_content", "llm_prompt"],
        metadata={"description": "output columns for source path, metadata, extracted fields, page text, and the llm_prompt bridge column used by downstream form-filling LLM steps; exactly 5 output_keys are mandatory, and llm_prompt must remain present even when include_bridge_prompt=False (it is then emitted as an empty string)"},
    )
    row_mode: str = field(
        default="per_pdf",
        metadata={"description": "row shape of emitted data: per_pdf emits one row per file, per_field emits one row per field"},
    )
    include_bridge_prompt: bool = field(
        default=True,
        metadata={"description": "whether to generate and emit an llm_prompt bridge string for each output row"},
    )
    emit_writable_only: bool = field(
        default=True,
        metadata={"description": "whether to keep only writable form fields and skip read-only or unsupported widgets"},
    )
    require_pdf_extension: bool = field(
        default=True,
        metadata={"description": "whether file paths must end with .pdf"},
    )
    label_search_left: float = field(
        default=90.0,
        metadata={"description": "horizontal label-search range in points to the left of each field rectangle"},
    )
    label_search_above: float = field(
        default=60.0,
        metadata={"description": "vertical label-search range in points above each field rectangle"},
    )
    label_search_right: float = field(
        default=20.0,
        metadata={"description": "horizontal label-search range in points to the right of each field rectangle"},
    )
    context_search_padding: float = field(
        default=140.0,
        metadata={"description": "padding in points around a field rectangle for selecting nearby page context text"},
    )

    @staticmethod
    def generate_llm_prompt(extracted_fields: list[dict[str, Any]]) -> str:
        """Build a strict bridge prompt for form-filling LLM calls.
    
        The prompt enforces JSON-only output and key fidelity to PDF field names.
        """
        if len(extracted_fields) == 0:
            return 'Return only this JSON object: {"field_updates": []}'
    
        lines: list[str] = [
            "You are a form-filling assistant.",
            "Answer each generated_question using the provided RAG context.",
            "Do not infer business meaning from internal_field_id alone; generated_question and question_context are authoritative.",
            "Treat current field values and visible example values from the PDF as untrusted local hints only.",
            "If retrieved context conflicts with prefilled PDF content, prefer the retrieved context.",
            "Return JSON only (no markdown, no code fences, no explanations).",
            "Return exactly one object with key field_updates (array).",
            "Each field update item must contain internal_field_id plus either value (text/list fields) or selected_state (checkbox/radio fields).",
            "For checkbox/radio, selected_state must be one of button_states.",
            "If context implies yes/no and button_states are non-obvious, map to the closest valid state token.",
            "If uncertain for a button field, use selected_state as an empty string.",
            "",
            "Fields:",
        ]
    
        template_updates: list[dict[str, str]] = []
        for idx, field_payload in enumerate(extracted_fields, start=1):
            internal_field_id = str(
                field_payload.get("internal_field_id", field_payload.get("write_target_field_id", field_payload.get("field_name", "")))
            ).strip()
            field_type = str(field_payload.get("field_type", "")).strip()
            generated_question = str(field_payload.get("generated_question", "")).strip()
            question_context = str(field_payload.get("question_context", field_payload.get("context_signature", ""))).strip()
            button_states_value = field_payload.get("button_states", [])
            button_states = button_states_value if isinstance(button_states_value, list) else []
            answer_key = "selected_state" if field_type in {"checkbox", "radio"} else "value"
            lines.append(
                f'{idx}. internal_field_id="{internal_field_id}" | type="{field_type}" | answer_key="{answer_key}" '
                f'| generated_question="{generated_question}" | question_context="{question_context}" '
                f'| button_states={json.dumps(button_states, ensure_ascii=True)}'
            )
            if internal_field_id == "":
                continue
            if field_type in {"checkbox", "radio"}:
                template_updates.append(
                    {
                        "internal_field_id": internal_field_id,
                        "selected_state": "<one_of_button_states_or_empty>",
                    }
                )
            else:
                template_updates.append(
                    {
                        "internal_field_id": internal_field_id,
                        "value": "<determined_value>",
                    }
                )
    
        template = {"field_updates": template_updates}
    
        lines.extend(
            [
                "",
                "Return JSON with exactly this shape and no extra top-level keys:",
                json.dumps(template, ensure_ascii=True, indent=2),
            ]
        )
        return "\n".join(lines)

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

    def _field_rows(self, fields: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        if self.row_mode == "per_pdf":
            return [fields]
        return [[]] if len(fields) == 0 else [[field_payload] for field_payload in fields]

    def _build_rows(self, file_path: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        fields = payload["fields"]
        rows: list[dict[str, Any]] = []
        for field_row in self._field_rows(fields):
            prompt = self.generate_llm_prompt(field_row) if self.include_bridge_prompt else ""
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
        fitz = _pdf_utils.import_fitz()
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
                page_text = _pdf_utils.clean_text(page.get_text("text"))
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
        except NodeException:
            raise
        except Exception as exc:
            raise NodeException("could not read pdf file " + str(file_path)) from exc
        finally:
            try:
                document.close()
            except Exception:
                pass

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
        field_type = _pdf_utils.classify_widget_type(widget, fitz)
        is_writable = self._is_writable_widget(widget, field_type)
        button_states = _pdf_utils.collect_button_states(widget)
        if field_type in self.BUTTON_FIELD_TYPES:
            visual_label = self._sanitize_label_text(self._infer_visual_label(rect, words, fitz))
        else:
            visual_label = self._sanitize_label_text(self._infer_text_visual_label(rect, words, fitz))
        if visual_label == "" and tooltip != "":
            visual_label = self._sanitize_label_text(tooltip)
        page_context = self._sanitize_context_text(self._infer_page_context(rect, blocks, fitz))
        option_text = self._sanitize_label_text(self._infer_option_text(rect, words, fitz, field_type, visual_label))
        question_text = self._sanitize_context_text(self._infer_question_text(rect, blocks, fitz))
        section_header = self._sanitize_context_text(self._infer_section_header(rect, blocks, fitz))
        context_signature = self._build_context_signature(
            section_header=section_header,
            question_text=question_text,
            option_text=option_text,
            visual_label=visual_label,
            page_context=page_context,
            tooltip=tooltip,
        )
        context_markers = self._extract_context_markers(context_signature)
        field_value = self._normalize_field_value(getattr(widget, "field_value", None))
        generated_question = self._synthesize_field_question(
            internal_field_id=field_name,
            field_type=field_type,
            tooltip=tooltip,
            visual_label=visual_label,
            option_text=option_text,
            question_text=question_text,
            section_header=section_header,
            page_context=page_context,
            button_states=button_states,
        )
        answer_key = "selected_state" if field_type in self.BUTTON_FIELD_TYPES else "value"

        return {
            "internal_field_id": field_name,
            "field_name": field_name,
            "write_target_field_id": field_name,
            "field_type": field_type,
            "answer_key": answer_key,
            "generated_question": generated_question,
            "question_context": context_signature,
            "field_value": field_value,
            "tooltip": tooltip,
            "visual_label": visual_label,
            "page_context": page_context,
            "option_text": option_text,
            "question_text": question_text,
            "section_header": section_header,
            "context_signature": context_signature,
            "context_markers": context_markers,
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
                cleaned = _pdf_utils.clean_text(str(value))
                if cleaned == "":
                    continue
                metadata[str(key)] = cleaned
        return metadata

    def _extract_text_rect_items(self, page: Any, mode: str, fitz: Any) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for row in page.get_text(mode) or []:
            if len(row) < 5:
                continue
            text = _pdf_utils.clean_text(str(row[4]))
            if text == "":
                continue
            items.append(
                {
                    "text": text,
                    "rect": fitz.Rect(float(row[0]), float(row[1]), float(row[2]), float(row[3])),
                }
            )
        return items

    def _extract_words(self, page: Any, fitz: Any) -> list[dict[str, Any]]:
        return self._extract_text_rect_items(page, "words", fitz)

    def _extract_blocks(self, page: Any, fitz: Any) -> list[dict[str, Any]]:
        return self._extract_text_rect_items(page, "blocks", fitz)

    def _resolve_field_name(self, document: Any, widget: Any) -> str:
        direct = _pdf_utils.clean_text(str(getattr(widget, "field_name", "") or ""))
        if direct != "":
            return direct
        return self._read_widget_pdf_key(document, widget, "T")

    def _resolve_tooltip(self, document: Any, widget: Any) -> str:
        label = _pdf_utils.clean_text(str(getattr(widget, "field_label", "") or ""))
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
        return _pdf_utils.clean_text(text)

    def _to_rect(self, widget: Any, fitz: Any) -> Any | None:
        rect = getattr(widget, "rect", None)
        if rect is None:
            return None
        try:
            return fitz.Rect(rect)
        except Exception:
            return None

    def _is_writable_widget(self, widget: Any, field_type: str) -> bool:
        if field_type in self.WRITABLE_FIELD_TYPES:
            if field_type in self.BUTTON_FIELD_TYPES and _pdf_utils.is_push_button(widget):
                return False
            return True
        return False

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
        return _pdf_utils.clean_text(str(value))

    def _infer_text_visual_label(self, field_rect: Any, words: list[dict[str, Any]], fitz: Any) -> str:
        candidates = [
            self._sanitize_label_text(self._infer_label_left_of_field(field_rect, words, fitz)),
            self._sanitize_label_text(self._infer_label_above_field(field_rect, words, fitz)),
            self._sanitize_label_text(self._infer_visual_label(field_rect, words, fitz)),
        ]
        return next((candidate for candidate in candidates if self._is_specific_field_label(candidate)), "") or next(
            (candidate for candidate in candidates if candidate != ""),
            "",
        )

    def _infer_label_above_field(self, field_rect: Any, words: list[dict[str, Any]], fitz: Any) -> str:
        search_rect = fitz.Rect(
            field_rect.x0 - 8.0,
            field_rect.y0 - min(float(self.label_search_above), 24.0),
            field_rect.x1 + 8.0,
            field_rect.y0 + 2.0,
        )
        candidates: list[dict[str, Any]] = []
        for word in words:
            word_rect = word["rect"]
            if not search_rect.intersects(word_rect):
                continue
            if self._overlap_ratio(word_rect, field_rect) > 0.15:
                continue
            center_x = (word_rect.x0 + word_rect.x1) / 2.0
            center_y = (word_rect.y0 + word_rect.y1) / 2.0
            if center_x < field_rect.x0 - 8.0 or center_x > field_rect.x1 + 8.0:
                continue
            score = abs(center_y - field_rect.y0) * 3.0
            candidates.append({"text": word["text"], "rect": word_rect, "score": score})

        if len(candidates) == 0:
            return ""
        return self._join_best_line(candidates)

    def _infer_label_left_of_field(self, field_rect: Any, words: list[dict[str, Any]], fitz: Any) -> str:
        search_rect = fitz.Rect(
            field_rect.x0 - max(float(self.label_search_left), 220.0),
            field_rect.y0 - 6.0,
            field_rect.x0 + 4.0,
            field_rect.y1 + 6.0,
        )
        candidates: list[dict[str, Any]] = []
        field_center_y = (field_rect.y0 + field_rect.y1) / 2.0
        for word in words:
            word_rect = word["rect"]
            if not search_rect.intersects(word_rect):
                continue
            if self._overlap_ratio(word_rect, field_rect) > 0.15:
                continue
            if float(word_rect.x1) > float(field_rect.x0) + 12.0:
                continue
            center_y = (word_rect.y0 + word_rect.y1) / 2.0
            if abs(center_y - field_center_y) > 10.0:
                continue
            distance = float(field_rect.x0) - float(word_rect.x1)
            candidates.append({"text": word["text"], "rect": word_rect, "score": distance})

        if len(candidates) == 0:
            return ""

        candidates.sort(key=lambda item: float(item["rect"].x0))
        rightmost = candidates[-1]["rect"]
        line_words = self._line_words(candidates, (rightmost.y0 + rightmost.y1) / 2.0)
        tail: list[dict[str, Any]] = []
        last_x = None
        for item in reversed(line_words):
            if last_x is not None and (last_x - float(item["rect"].x1)) > 26.0:
                break
            tail.append(item)
            last_x = float(item["rect"].x0)
        tail.reverse()
        return self._join_text_items(tail)

    def _line_words(self, items: list[dict[str, Any]], anchor_y: float, tolerance: float = 4.5) -> list[dict[str, Any]]:
        line_words = [
            item for item in items if abs(((item["rect"].y0 + item["rect"].y1) / 2.0) - anchor_y) <= tolerance
        ]
        line_words.sort(key=lambda item: float(item["rect"].x0))
        return line_words

    def _join_text_items(self, items: list[dict[str, Any]]) -> str:
        return _pdf_utils.clean_text(" ".join(item["text"] for item in items))

    def _join_best_line(self, candidates: list[dict[str, Any]]) -> str:
        ordered = sorted(candidates, key=lambda item: float(item["score"]))
        anchor_rect = ordered[0]["rect"]
        return self._join_text_items(self._line_words(ordered, (anchor_rect.y0 + anchor_rect.y1) / 2.0))

    def _overlap_ratio(self, rect_a: Any, rect_b: Any) -> float:
        try:
            intersection = rect_a & rect_b
        except Exception:
            return 0.0
        if intersection is None or getattr(intersection, "is_empty", False):
            return 0.0
        try:
            area_a = max(float(rect_a.width) * float(rect_a.height), 0.0)
            if area_a <= 0.0:
                return 0.0
            return max(float(intersection.width) * float(intersection.height), 0.0) / area_a
        except Exception:
            return 0.0

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
            if self._overlap_ratio(word_rect, field_rect) > 0.25:
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
        return self._join_text_items(self._line_words(candidates, (anchor_rect.y0 + anchor_rect.y1) / 2.0))

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
            text = _pdf_utils.clean_text(str(block.get("text", "")))
            if self._is_context_noise(text):
                continue
            if self._overlap_ratio(block_rect, field_rect) > 0.20:
                continue
            if block_rect.y1 <= field_rect.y0 + 2.0:
                overlap = min(block_rect.x1, field_rect.x1 + padding) - max(block_rect.x0, field_rect.x0 - padding)
                if overlap >= -2.0:
                    distance = field_rect.y0 - block_rect.y1
                    above_candidates.append({"text": text, "distance": distance})
            if context_rect.intersects(block_rect):
                center_x = (block_rect.x0 + block_rect.x1) / 2.0
                center_y = (block_rect.y0 + block_rect.y1) / 2.0
                field_center_x = (field_rect.x0 + field_rect.x1) / 2.0
                field_center_y = (field_rect.y0 + field_rect.y1) / 2.0
                distance = abs(center_x - field_center_x) + abs(center_y - field_center_y)
                near_candidates.append({"text": text, "distance": distance})

        if len(above_candidates) > 0:
            above_candidates.sort(key=lambda item: float(item["distance"]))
            return self._truncate_context(above_candidates[0]["text"])
        if len(near_candidates) > 0:
            near_candidates.sort(key=lambda item: float(item["distance"]))
            return self._truncate_context(near_candidates[0]["text"])
        return ""

    def _infer_option_text(
        self,
        field_rect: Any,
        words: list[dict[str, Any]],
        fitz: Any,
        field_type: str,
        fallback_label: str,
    ) -> str:
        if field_type not in self.BUTTON_FIELD_TYPES:
            return fallback_label

        line_rect = fitz.Rect(
            field_rect.x0 - 4.0,
            field_rect.y0 - 6.0,
            field_rect.x1 + 520.0,
            field_rect.y1 + 6.0,
        )
        target_y = (field_rect.y0 + field_rect.y1) / 2.0
        line_words: list[dict[str, Any]] = []
        for word in words:
            word_rect = word["rect"]
            if not line_rect.intersects(word_rect):
                continue
            if float(word_rect.x1) < float(field_rect.x0) - 4.0:
                continue
            center_y = (word_rect.y0 + word_rect.y1) / 2.0
            if abs(center_y - target_y) > 6.0:
                continue
            line_words.append(word)

        if len(line_words) == 0:
            return fallback_label

        line_words.sort(key=lambda item: float(item["rect"].x0))
        return self._join_text_items(line_words)

    def _candidate_blocks_above(
        self,
        field_rect: Any,
        blocks: list[dict[str, Any]],
        left_pad: float = 260.0,
        right_pad: float = 260.0,
        max_distance: float | None = None,
    ) -> list[dict[str, Any]]:
        left = float(field_rect.x0) - left_pad
        right = float(field_rect.x1) + right_pad
        candidates: list[dict[str, Any]] = []
        for block in blocks:
            block_rect = block["rect"]
            if block_rect.y1 > field_rect.y0 + 2.0:
                continue
            if self._overlap_ratio(block_rect, field_rect) > 0.20:
                continue
            overlap = min(block_rect.x1, right) - max(block_rect.x0, left)
            if overlap < -8.0:
                continue
            distance = field_rect.y0 - block_rect.y1
            if max_distance is not None and distance > max_distance:
                continue
            text = _pdf_utils.clean_text(str(block.get("text", "")))
            if self._is_context_noise(text):
                continue
            candidates.append({"text": text, "distance": distance})
        candidates.sort(key=lambda item: float(item["distance"]))
        return candidates

    def _infer_question_text(self, field_rect: Any, blocks: list[dict[str, Any]], fitz: Any) -> str:
        candidates = self._candidate_blocks_above(field_rect, blocks)
        for item in candidates:
            text = _pdf_utils.clean_text(item["text"])
            if text == "":
                continue
            if re.match(r"^\d+\s+\S+", text) and len(text) < 120:
                continue
            return self._truncate_context(text, max_len=280)
        if len(candidates) > 0:
            return self._truncate_context(str(candidates[0]["text"]), max_len=280)
        return ""

    def _infer_section_header(self, field_rect: Any, blocks: list[dict[str, Any]], fitz: Any) -> str:
        candidates = self._candidate_blocks_above(field_rect, blocks, max_distance=260.0)
        for item in candidates:
            text = _pdf_utils.clean_text(item["text"])
            if text == "":
                continue
            if self._looks_like_section_header(text):
                return self._truncate_context(text, max_len=180)
        for item in candidates:
            text = _pdf_utils.clean_text(item["text"])
            if text == "":
                continue
            if len(text) <= 120:
                return self._truncate_context(text, max_len=180)
        return ""

    def _build_context_signature(
        self,
        section_header: str,
        question_text: str,
        option_text: str,
        visual_label: str,
        page_context: str,
        tooltip: str,
    ) -> str:
        pieces = [section_header, question_text, option_text, visual_label, page_context, tooltip]
        signature_parts: list[str] = []
        seen: set[str] = set()
        for piece in pieces:
            cleaned = _pdf_utils.clean_text(piece)
            if cleaned == "":
                continue
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            signature_parts.append(cleaned)
        return self._truncate_context(" | ".join(signature_parts), max_len=420)

    def _synthesize_field_question(
        self,
        internal_field_id: str,
        field_type: str,
        tooltip: str,
        visual_label: str,
        option_text: str,
        question_text: str,
        section_header: str,
        page_context: str,
        button_states: list[str],
    ) -> str:
        if field_type in self.BUTTON_FIELD_TYPES:
            scope = self._first_non_empty(question_text, section_header, page_context, "this section")
            option = self._first_non_empty(option_text, visual_label, tooltip, internal_field_id)
            states_text = ", ".join(button_states) if len(button_states) > 0 else "Off"
            return (
                'For section "' + self._clean_for_question(scope) + '", which state should be selected for option "'
                + self._clean_for_question(option)
                + '"? Return one of: '
                + states_text
            )

        semantic_subject = self._infer_semantic_subject(
            internal_field_id=internal_field_id,
            tooltip=tooltip,
            visual_label=visual_label,
            option_text=option_text,
            question_text=question_text,
            section_header=section_header,
            page_context=page_context,
        )
        if semantic_subject != "":
            return "What is " + semantic_subject + "?"

        subject = self._first_non_empty(tooltip, visual_label, question_text, section_header, internal_field_id)
        clean_subject = self._clean_for_question(subject)
        if ":" in clean_subject:
            clean_subject = self._clean_for_question(clean_subject.split(":")[0])
        if clean_subject == "":
            clean_subject = "this field"
        return 'What value should be written into "' + clean_subject + '"?'

    def _first_non_empty(self, *values: str) -> str:
        return next(
            (
                cleaned
                for value in values
                for cleaned in [_pdf_utils.clean_text(str(value))]
                if cleaned != "" and not self._is_placeholder_text(cleaned)
            ),
            "",
        )

    def _sanitize_label_text(self, text: str) -> str:
        clean = _pdf_utils.clean_text(text)
        if self._is_placeholder_text(clean):
            return ""
        clean = clean.strip(" -;,.")
        clean = re.sub(r"^[>\-\u2022\u25cf\u25ba\u00da]+\s*", "", clean)
        if ":" in clean:
            prefix, suffix = clean.split(":", 1)
            prefix = _pdf_utils.clean_text(prefix)
            suffix = _pdf_utils.clean_text(suffix)
            if prefix != "" and self._looks_like_inline_value(suffix):
                clean = prefix
        clean = re.sub(r"\s{2,}", " ", clean).strip(" -:;,.")
        return "" if self._is_placeholder_text(clean) else clean

    def _sanitize_context_text(self, text: str) -> str:
        clean = self._sanitize_label_text(text)
        if self._is_context_noise(clean):
            return ""
        return clean

    def _is_specific_field_label(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        if clean == "":
            return False
        if self._is_context_noise(clean):
            return False
        if self._looks_like_section_header(clean):
            return False
        return len(clean) <= 80

    def _looks_like_inline_value(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        if clean == "":
            return False
        if re.search(r"\d", clean):
            return True
        tokens = clean.split()
        if len(tokens) >= 4 and all(len(token) == 1 for token in tokens if token.isalnum()):
            return True
        if len(tokens) >= 2 and any(token.isupper() for token in tokens):
            return True
        return False

    def _is_context_noise(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        if self._is_placeholder_text(clean):
            return True
        if re.fullmatch(r"[0-9 ]+", clean):
            return True
        if clean.startswith(">>>"):
            return True
        folded = _pdf_utils.ascii_fold(clean.lower())
        if folded in {"ja", "nein", "off", "ledig", "verheiratet", "verwitwet", "geschieden", "weitere", "nach"}:
            return True
        return False

    def _looks_like_section_header(self, text: str) -> bool:
        clean = _pdf_utils.clean_text(text)
        if self._is_placeholder_text(clean):
            return False
        folded = _pdf_utils.ascii_fold(clean)
        if re.match(r"^\d{1,2}\s+[A-Za-z]", folded):
            return True
        return False

    def _infer_semantic_subject(
        self,
        internal_field_id: str,
        tooltip: str,
        visual_label: str,
        option_text: str,
        question_text: str,
        section_header: str,
        page_context: str,
    ) -> str:
        folded_id = _pdf_utils.ascii_fold(str(internal_field_id).lower())
        primary = _pdf_utils.ascii_fold(
            " | ".join([str(tooltip), str(visual_label), str(option_text)]).lower()
        )
        secondary = _pdf_utils.ascii_fold(
            " | ".join([str(question_text), str(section_header), str(page_context)]).lower()
        )

        id_subject = self._match_semantic_subject(folded_id, field_scope=secondary)
        if id_subject != "":
            return id_subject
        primary_subject = self._match_semantic_subject(primary, field_scope=secondary)
        if primary_subject != "":
            return primary_subject
        secondary_subject = self._match_semantic_subject(secondary, field_scope=secondary)
        if secondary_subject != "":
            return secondary_subject
        return ""

    def _match_semantic_subject(self, folded: str, field_scope: str = "") -> str:
        scope = _pdf_utils.ascii_fold(str(field_scope).lower())
        if folded == "":
            return ""
        return ""

    def _clean_for_question(self, text: str) -> str:
        cleaned = _pdf_utils.clean_text(text)
        cleaned = cleaned.strip(" -:;,.")
        return cleaned

    def _is_placeholder_text(self, text: str) -> bool:
        lowered = _pdf_utils.clean_text(str(text)).strip().lower()
        return lowered in {"", "null", "none", "nan", "n/a", "na", "off", "-", "--"}

    def _extract_context_markers(self, context_signature: str) -> list[str]:
        folded = _pdf_utils.ascii_fold(context_signature.lower())
        return list(dict.fromkeys(re.findall(r"[a-z0-9]{3,}", folded)))[:24]

    def _truncate_context(self, text: str, max_len: int = 220) -> str:
        clean = _pdf_utils.clean_text(text)
        if len(clean) <= max_len:
            return clean
        return clean[:max_len].rstrip() + "..."
