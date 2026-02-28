from dataclasses import dataclass, field
import re
from typing import Any

from pypdf import PdfReader

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class ReadPDFFormAction(BufferNode, Action):
    """Read native PDF AcroForm fields for form-filling workflows.

    Purpose:
    This action is intended for PDF *form field* extraction and closed-loop
    read->fill->write pipelines with `WritePDFFormAction`.

    Not OCR:
    Use `OCRAction` or `LLMOCRAction` for OCR-like full-text extraction from
    arbitrary PDFs/images. This action focuses on native AcroForm widgets.
    """

    input_keys: list[str] = field(
        default_factory=lambda: ["values"],
        metadata={
            "description": "Keys used to extract PDF paths from parent data. "
            "If empty, all parent keys are considered."
        },
    )
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "metadata", "fields", "full_text_content"],
        metadata={
            "description": "Output keys in fixed order [filepath, metadata, fields, full_text_content]. "
            "Exactly four keys are required."
        },
    )
    fields_output_mode: str = field(
        default="per_pdf",
        metadata={
            "description": "Row emission mode: 'per_pdf' emits one row per PDF with all fields; "
            "'per_field' emits one row per field with a one-item `fields` list."
        },
    )
    label_y_tolerance: float = field(
        default=18.0,
        metadata={
            "description": "Vertical tolerance in PDF points for same-row context matching."
        },
    )
    label_max_tokens: int = field(
        default=6,
        metadata={
            "description": "Maximum tokens retained in legacy `label_context`."
        },
    )
    require_pdf_extension: bool = field(
        default=True,
        metadata={
            "description": "If True, reject non-.pdf inputs before parsing."
        },
    )
    emit_fillable_only: bool = field(
        default=True,
        metadata={
            "description": "If True, only emit fields that are writable/fillable."
        },
    )
    include_context_bundle: bool = field(
        default=True,
        metadata={
            "description": "If True, emit `context_bundle` with deterministic label candidates and metadata."
        },
    )
    include_retrieval_query: bool = field(
        default=True,
        metadata={
            "description": "If True, emit deterministic `retrieval_query` per field for RAG retrieval."
        },
    )
    context_candidate_window: float = field(
        default=60.0,
        metadata={
            "description": "Geometry window in PDF points used for nearby context candidate collection."
        },
    )
    context_min_confidence: float = field(
        default=0.45,
        metadata={
            "description": "Minimum context confidence threshold. Below this, `needs_review=True`."
        },
    )

    def _on_install(self, agent: Agent = None):
        """Install and validate output/schema constraints."""
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        if len(self.output_keys) != 4:
            raise NodeException(
                f"{self.cname()} requires exactly 4 output_keys, got {len(self.output_keys)}"
            )
        if self.fields_output_mode not in {"per_field", "per_pdf"}:
            raise NodeException("fields_output_mode must be either 'per_field' or 'per_pdf'")
        if self.context_candidate_window <= 0:
            raise NodeException("context_candidate_window must be > 0")
        if self.context_min_confidence < 0 or self.context_min_confidence > 1:
            raise NodeException("context_min_confidence must be between 0 and 1")

    def _on_execute(self):
        """Read parent-provided PDF paths, extract structured content, and push rows according to `fields_output_mode`."""
        file_paths = self._extract_paths_from_parent_data(self.get_parent_data())
        if len(file_paths) == 0:
            raise NodeException("No PDF file paths were found in parent buffer data")

        for file_path in file_paths:
            if not FileUtils.exists_file(file_path):
                raise NodeException("filepath " + file_path + " does not exist")
            if self.require_pdf_extension and not file_path.lower().endswith(".pdf"):
                raise NodeException("filepath " + file_path + " is not a PDF file")

            pdf_result = self._read_pdf(file_path)
            fields = pdf_result["fields"]
            field_rows = self._build_field_rows(fields)

            for row_fields in field_rows:
                row = dict(
                    zip(
                        self.output_keys,
                        [
                            file_path,
                            pdf_result["metadata"],
                            row_fields,
                            pdf_result["full_text_content"],
                        ],
                    )
                )
                # Push one row batch to preserve list-valued cells like `fields`.
                self.add_data({key: [value] for key, value in row.items()})

    def _build_field_rows(self, fields: list[dict]) -> list[list[dict]]:
        """Build output rows according to configured field row emission mode."""
        if self.fields_output_mode == "per_pdf":
            return [list(fields)]
        if len(fields) == 0:
            return [[]]
        return [[field] for field in fields]

    def _read_pdf(self, file_path: str) -> dict:
        """Parse one PDF into metadata, AcroForm fields, and full text.

        Limitation:
        Only AcroForm fields are extracted. No virtual placeholder inference is applied.
        """
        try:
            reader = PdfReader(file_path)
        except Exception as e:
            raise NodeException("could not read pdf file " + file_path) from e

        page_data = [self._read_page(page) for page in reader.pages]
        full_text = "\n".join([d["text"] for d in page_data if d["text"]]).strip()
        spans_by_page = [d["spans"] for d in page_data]
        fields = self._extract_fields(reader, spans_by_page)

        return {
            "metadata": self._normalize_metadata(reader),
            "fields": fields,
            "full_text_content": full_text,
        }

    def _extract_paths_from_parent_data(self, data: dict) -> list[str]:
        """Select configured input keys and flatten their values into a list of file paths."""
        if not data:
            return []

        keys = self.input_keys if len(self.input_keys) > 0 else list(data.keys())
        paths: list[str] = []
        for key in keys:
            if key in data:
                self._collect_paths(data[key], paths)
        return paths

    def _collect_paths(self, value: Any, target: list[str]):
        """Recursively flatten nested iterables of paths and validate each string path."""
        if isinstance(value, str):
            path = value.strip()
            if path == "":
                raise NodeException("empty file path in parent data")
            target.append(path)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect_paths(item, target)
        else:
            raise NodeException(
                "unsupported parent data type for file path extraction: " + str(type(value))
            )

    def _extract_fields(self, reader: PdfReader, spans_by_page: list[list[dict]]) -> list[dict]:
        """Build context-rich form field records from AcroForm + widget annotations."""
        field_map: dict[str, dict] = {}

        form_fields = reader.get_fields() or {}
        for field_name, field_data in form_fields.items():
            normalized_name = str(field_name)
            field_type = self._to_serializable(self._get_value(field_data, "/FT")) or ""
            field_map[normalized_name] = {
                "field_id": normalized_name,
                "write_target_field_id": normalized_name,
                "field_type": field_type,
                "explicit_label": self._to_serializable(self._get_value(field_data, "/TU")) or "",
                "current_value": self._to_serializable(self._get_value(field_data, "/V")) or "",
                "rect": self._normalize_rect(self._get_value(field_data, "/Rect")),
                "page_index": -1,
                "field_flags": self._to_serializable(self._get_value(field_data, "/Ff")),
                "is_fillable": self._is_fillable_field(field_type, field_data, None),
            }

        for page_idx, page in enumerate(reader.pages):
            annots = self._resolve_annotation_list(self._get_value(page, "/Annots"))
            if len(annots) == 0:
                continue

            for annot_ref in annots:
                annot = self._resolve_pdf_object(annot_ref)
                if str(self._get_value(annot, "/Subtype")) != "/Widget":
                    continue

                parent = self._resolve_pdf_object(self._get_value(annot, "/Parent"))
                field_name = self._coalesce(
                    self._to_serializable(self._get_value(parent, "/T")),
                    self._to_serializable(self._get_value(annot, "/T")),
                )
                if field_name is None:
                    field_name = f"field_{page_idx}_{len(field_map)}"
                field_name = str(field_name)

                field_type = self._coalesce(
                    self._to_serializable(self._get_value(annot, "/FT")),
                    self._to_serializable(self._get_value(parent, "/FT")),
                    "",
                )
                rect = self._normalize_rect(
                    self._coalesce(
                        self._get_value(annot, "/Rect"),
                        self._get_value(parent, "/Rect"),
                    )
                )
                field_flags = self._coalesce(
                    self._to_serializable(self._get_value(annot, "/Ff")),
                    self._to_serializable(self._get_value(parent, "/Ff")),
                    "",
                )
                incoming = {
                    "field_id": field_name,
                    "write_target_field_id": field_name,
                    "field_type": field_type,
                    "explicit_label": self._coalesce(
                        self._to_serializable(self._get_value(annot, "/TU")),
                        self._to_serializable(self._get_value(parent, "/TU")),
                        "",
                    ),
                    "current_value": self._coalesce(
                        self._to_serializable(self._get_value(annot, "/V")),
                        self._to_serializable(self._get_value(parent, "/V")),
                        "",
                    ),
                    "rect": rect,
                    "page_index": page_idx,
                    "field_flags": field_flags,
                    "is_fillable": self._is_fillable_field(field_type, annot, parent),
                }
                field_map[field_name] = self._merge_field_record(field_map.get(field_name), incoming)

        fields: list[dict] = []
        for record in field_map.values():
            page_index = int(record.get("page_index", -1))
            spans = (
                spans_by_page[page_index]
                if page_index >= 0 and page_index < len(spans_by_page)
                else []
            )
            context = self._build_context_bundle(record, spans)
            enriched = self._build_enriched_field(record, context)
            if self.emit_fillable_only and not bool(enriched.get("is_fillable")):
                continue
            fields.append(enriched)

        return fields

    def _read_page(self, page) -> dict:
        """Extract both plain page text and positioned text spans in a single pass."""
        spans = []

        def visitor_text(text, cm, tm, font_dict, font_size):
            if text is None:
                return
            clean = " ".join(str(text).split())
            if clean == "":
                return

            x = 0.0
            y = 0.0
            try:
                if tm is not None and len(tm) >= 6:
                    x = float(tm[4])
                    y = float(tm[5])
                elif cm is not None and len(cm) >= 6:
                    x = float(cm[4])
                    y = float(cm[5])
            except Exception:
                pass
            spans.append({"text": clean, "x": x, "y": y})

        try:
            text = page.extract_text(visitor_text=visitor_text) or ""
        except TypeError:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        if len(spans) == 0 and text:
            clean = " ".join(text.split())
            if clean:
                spans.append({"text": clean, "x": 0.0, "y": 0.0})

        return {"text": text.strip(), "spans": spans}

    def _resolve_annotation_list(self, annots: Any) -> list[Any]:
        """Normalize annotation arrays into Python lists."""
        resolved = self._resolve_pdf_object(annots)
        if resolved is None:
            return []
        try:
            return list(resolved)
        except Exception:
            return []

    def _merge_field_record(self, existing: dict | None, incoming: dict) -> dict:
        """Merge two partial field records with stable, non-empty-first semantics."""
        if existing is None:
            return dict(incoming)

        merged = dict(existing)
        merged["field_id"] = str(
            self._coalesce(existing.get("field_id"), incoming.get("field_id"), "field_unknown")
        )
        merged["write_target_field_id"] = str(
            self._coalesce(
                existing.get("write_target_field_id"),
                incoming.get("write_target_field_id"),
                merged["field_id"],
            )
        )
        merged["field_type"] = self._coalesce(existing.get("field_type"), incoming.get("field_type"), "")
        merged["explicit_label"] = self._coalesce(
            existing.get("explicit_label"),
            incoming.get("explicit_label"),
            "",
        )
        merged["current_value"] = self._coalesce(
            existing.get("current_value"),
            incoming.get("current_value"),
            "",
        )
        merged["rect"] = existing.get("rect") if existing.get("rect") is not None else incoming.get("rect")
        existing_page = int(existing.get("page_index", -1))
        incoming_page = int(incoming.get("page_index", -1))
        merged["page_index"] = existing_page if existing_page >= 0 else incoming_page
        merged["field_flags"] = self._coalesce(existing.get("field_flags"), incoming.get("field_flags"), "")
        merged["is_fillable"] = bool(existing.get("is_fillable")) or bool(incoming.get("is_fillable"))
        return merged

    def _build_enriched_field(self, record: dict, context: dict) -> dict:
        """Create final emitted field payload (legacy + enriched keys)."""
        primary_label = str(context.get("primary_label", "")).strip()
        label_context = self._truncate_tokens(primary_label)
        current_value = self._to_serializable(record.get("current_value"))
        if current_value is None:
            current_value = ""

        confidence = float(context.get("confidence", 0.0))
        needs_review = confidence < self.context_min_confidence
        retrieval_query = self._build_retrieval_query(record, context) if self.include_retrieval_query else ""
        context_bundle = context if self.include_context_bundle else {}

        return {
            "field_id": str(record.get("field_id", "")),
            "write_target_field_id": str(
                self._coalesce(record.get("write_target_field_id"), record.get("field_id"), "")
            ),
            "field_type": str(record.get("field_type", "")),
            "label_context": label_context,
            "current_value": current_value,
            "proposed_value": "",
            "rect": record.get("rect"),
            "is_fillable": bool(record.get("is_fillable")),
            "page_index": int(record.get("page_index", -1)),
            "context_bundle": context_bundle,
            "value_profile": self._build_value_profile(str(record.get("field_type", "")), current_value),
            "retrieval_query": retrieval_query,
            "context_confidence": max(0.0, min(confidence, 1.0)),
            "needs_review": needs_review,
        }

    def _build_context_bundle(self, record: dict, spans: list[dict]) -> dict:
        """Build deterministic contextual metadata for one field record."""
        explicit_label_value = record.get("explicit_label")
        explicit_label = "" if explicit_label_value is None else str(explicit_label_value).strip()
        rect = record.get("rect")
        candidates = self._collect_context_candidates(rect, spans)

        primary_label = explicit_label
        source = "tu" if explicit_label != "" else ""
        confidence = 1.0 if explicit_label != "" else 0.0
        supporting: list[str] = []

        if primary_label == "":
            if len(candidates) > 0:
                primary_label = str(candidates[0]["text"]).strip()
                source = str(candidates[0]["source"])
                confidence = float(candidates[0]["score"])
                supporting = [str(c["text"]) for c in candidates[1:4]]
            else:
                legacy = self._infer_label_context(rect, spans)
                primary_label = legacy
                source = "legacy"
                confidence = 0.2 if legacy else 0.0
        else:
            supporting = [str(c["text"]) for c in candidates[0:3]]

        section_hint = ""
        for candidate in candidates:
            if str(candidate.get("source", "")) == "above":
                section_hint = str(candidate.get("text", "")).strip()
                if section_hint != "":
                    break

        return {
            "primary_label": primary_label,
            "supporting_texts": supporting,
            "section_hint": section_hint,
            "source": source,
            "confidence": max(0.0, min(confidence, 1.0)),
            "candidates": candidates[0:5],
        }

    def _collect_context_candidates(self, rect: list[float] | None, spans: list[dict]) -> list[dict]:
        """Collect context candidates around a field by deterministic geometry rules."""
        if rect is None or len(rect) < 4 or len(spans) == 0:
            return []

        left_x = float(rect[0])
        bottom_y = float(rect[1])
        right_x = float(rect[2])
        top_y = float(rect[3])
        center_y = (bottom_y + top_y) / 2.0
        window = float(self.context_candidate_window)
        y_tol = float(self.label_y_tolerance)

        scored: dict[str, dict] = {}
        for span in spans:
            text = str(span.get("text", "")).strip()
            if text == "":
                continue
            x = float(span.get("x", 0.0))
            y = float(span.get("y", 0.0))
            y_delta = abs(y - center_y)
            local: list[tuple[str, float]] = []

            if x <= left_x and y_delta <= y_tol and (left_x - x) <= window * 2:
                score = 0.95 - (y_delta / max(y_tol, 1.0)) * 0.35 - ((left_x - x) / max(window * 2, 1.0)) * 0.25
                local.append(("left", score))

            if y >= top_y and (y - top_y) <= window and x >= (left_x - window) and x <= (right_x + window):
                score = 0.80 - ((y - top_y) / max(window, 1.0)) * 0.30 - (abs(x - left_x) / max(window * 2, 1.0)) * 0.10
                local.append(("above", score))

            if y_delta <= y_tol and x >= (left_x - window) and x <= (right_x + window):
                score = 0.60 - (y_delta / max(y_tol, 1.0)) * 0.20
                local.append(("row", score))

            if y > center_y and (y - center_y) <= (window * 2) and x < left_x:
                score = 0.50 - ((y - center_y) / max(window * 2, 1.0)) * 0.25
                local.append(("section", score))

            for source, score in local:
                if score <= 0.01:
                    continue
                existing = scored.get(text)
                if existing is None or float(existing["score"]) < score:
                    scored[text] = {"text": text, "score": round(score, 4), "source": source}

        ranked = list(scored.values())
        ranked.sort(key=lambda c: (-float(c["score"]), str(c["text"])))
        return ranked

    def _build_retrieval_query(self, record: dict, context: dict) -> str:
        """Build deterministic retrieval query text for downstream RAG lookup."""
        parts: list[str] = []
        write_target = str(record.get("write_target_field_id", "")).strip()
        primary_label = str(context.get("primary_label", "")).strip()
        section_hint = str(context.get("section_hint", "")).strip()
        shape_class = str(
            self._build_value_profile(str(record.get("field_type", "")), record.get("current_value")).get("shape_class", "")
        ).strip()

        if write_target:
            parts.append(write_target.replace("-", " "))
        if primary_label:
            parts.append(primary_label)
        if section_hint:
            parts.append(section_hint)
        if shape_class:
            parts.append("expected " + shape_class)

        deduped: list[str] = []
        seen: set[str] = set()
        for part in parts:
            normalized = " ".join(part.split())
            if normalized == "":
                continue
            low = normalized.lower()
            if low in seen:
                continue
            seen.add(low)
            deduped.append(normalized)
        return " | ".join(deduped)

    def _build_value_profile(self, field_type: str, value: Any) -> dict:
        """Create generic value-shape metadata without domain-specific semantic labels."""
        value_text = str(value).strip() if value is not None else ""
        return {
            "shape_class": self._detect_shape_class(field_type, value_text),
            "char_pattern": self._char_pattern(value_text),
            "length_hint": {
                "min_len": len(value_text) if value_text else 0,
                "max_len": len(value_text) if value_text else 0,
            },
            "allowed_options": self._infer_allowed_options(field_type),
        }

    def _detect_shape_class(self, field_type: str, value_text: str) -> str:
        """Infer generic value shape from field type and current value content."""
        ft = str(field_type)
        clean = value_text.strip()
        lowered = clean.lower()
        if ft == "/Btn":
            return "boolean_like"
        if ft == "/Ch":
            return "choice_like"
        if ft == "/Sig":
            return "signature_like"
        if clean == "":
            return "free_text" if ft in {"/Tx", "/Text"} else "unknown"
        if re.fullmatch(r"\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}", clean):
            return "date_like"
        if lowered in {"yes", "no", "true", "false", "x", "on", "off", "0", "1"}:
            return "boolean_like"
        if re.fullmatch(r"[+-]?\d+(\.\d+)?", clean):
            return "numeric_token"
        if " " in clean:
            return "multi_token"
        if re.fullmatch(r"[A-Za-z0-9]+", clean):
            return "single_token"
        return "free_text"

    def _char_pattern(self, value_text: str) -> str:
        """Convert text into simplified character-class pattern (A/9/literals)."""
        if value_text == "":
            return ""
        pattern: list[str] = []
        for ch in value_text[0:64]:
            if ch.isdigit():
                pattern.append("9")
            elif ch.isalpha():
                pattern.append("A")
            elif ch.isspace():
                pattern.append(" ")
            else:
                pattern.append(ch)
        return "".join(pattern)

    def _infer_allowed_options(self, field_type: str) -> list[str] | None:
        """Return generic option hints if they can be inferred from field type."""
        if str(field_type) == "/Btn":
            return ["yes", "no"]
        return None

    def _is_fillable_field(self, field_type: Any, annot: Any, parent: Any) -> bool:
        """Return True when a field is writable in typical AcroForm filling flows."""
        ft = str(field_type) if field_type is not None else ""
        if ft in {"/Tx", "/Text", "/Ch", "/Choice"}:
            return True
        if ft == "/Btn":
            flags = self._extract_field_flags(annot, parent)
            if flags is not None and self._is_push_button(flags):
                return False
            return True
        return False

    def _extract_field_flags(self, annot: Any, parent: Any) -> int | None:
        """Extract `/Ff` flags as integer when available."""
        raw = self._coalesce(
            self._to_serializable(self._get_value(annot, "/Ff")) if annot is not None else None,
            self._to_serializable(self._get_value(parent, "/Ff")) if parent is not None else None,
        )
        if raw is None:
            return None
        try:
            return int(raw)
        except Exception:
            return None

    def _is_push_button(self, field_flags: int) -> bool:
        """Check push-button bit (1 << 16) to exclude non-fillable action buttons."""
        return (int(field_flags) & 65536) != 0

    def _truncate_tokens(self, text: str) -> str:
        """Trim text to configured token limit for legacy `label_context` compatibility."""
        clean = " ".join(str(text).split())
        if clean == "":
            return ""
        return " ".join(clean.split()[0 : self.label_max_tokens])

    def _infer_label_context(self, rect: list[float] | None, spans: list[dict]) -> str:
        """Infer the best nearby label text for a field rectangle using y-distance and left-side bias."""
        if rect is None or len(rect) < 4 or len(spans) == 0:
            return ""

        left_x = float(rect[0])
        center_y = (float(rect[1]) + float(rect[3])) / 2.0

        best_text = ""
        best_score = None
        for span in spans:
            text = str(span.get("text", "")).strip()
            if text == "":
                continue
            x = float(span.get("x", 0.0))
            y = float(span.get("y", 0.0))
            y_delta = abs(y - center_y)
            if y_delta > self.label_y_tolerance:
                continue

            # Prefer text to the left side of the field and closest in vertical alignment.
            x_penalty = left_x - x if x <= left_x else (x - left_x) + 1000.0
            score = y_delta * 100.0 + x_penalty
            if best_score is None or score < best_score:
                best_score = score
                best_text = text

        if best_text == "":
            return ""
        return " ".join(best_text.split()[0 : self.label_max_tokens])

    def _to_serializable(self, value: Any) -> Any:
        """Normalize PDF object values into plain Python primitives/containers."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        if isinstance(value, (list, tuple)):
            return [self._to_serializable(v) for v in value]
        if isinstance(value, dict):
            return {str(k).lstrip("/"): self._to_serializable(v) for k, v in value.items()}
        return str(value)

    def _resolve_pdf_object(self, obj: Any) -> Any:
        """Dereference pypdf indirect objects when possible."""
        if obj is None:
            return None
        if hasattr(obj, "get_object"):
            try:
                return obj.get_object()
            except Exception:
                return obj
        return obj

    def _get_value(self, obj: Any, key: str, default: Any = None) -> Any:
        """Safely read a key from pypdf objects/dicts."""
        if obj is None:
            return default
        try:
            return obj.get(key, default)
        except Exception:
            return default

    def _normalize_metadata(self, reader: PdfReader) -> dict:
        """Collect normalized document metadata and always include page count."""
        metadata = {"pages": len(reader.pages)}
        raw_metadata = reader.metadata
        if raw_metadata:
            for key, value in raw_metadata.items():
                metadata[str(key).lstrip("/")] = self._to_serializable(value)
        return metadata

    def _normalize_rect(self, rect: Any) -> list[float] | None:
        """Convert PDF rectangle values into [x0, y0, x1, y1] floats when possible."""
        if rect is None:
            return None

        try:
            values = [float(item) for item in list(rect)[0:4]]
            return values if len(values) == 4 else None
        except Exception:
            return None

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
