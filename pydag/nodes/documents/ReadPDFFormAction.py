from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from pypdf import PdfReader

from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class ReadPDFFormAction(BufferNode, Action):
    """`Action` that extracts AcroForm fields and text from PDFs.

    Limitation:
    This action only extracts native PDF AcroForm data. PDFs without AcroForm fields
    return an empty `fields` list.
    """

    input_keys: list[str] = field(
        default_factory=lambda: ["values"],
        metadata={"description": "keys to read file paths from parent buffer data"},
    )
    output_keys: list[str] = field(
        default_factory=lambda: ["filepath", "metadata", "fields", "full_text_content"],
        metadata={
            "description": "output keys in the order [filepath, metadata, fields, full_text_content]"
        },
    )
    label_y_tolerance: float = field(
        default=18.0,
        metadata={
            "description": "Maximum vertical distance (PDF points) between a form field and nearby text considered as label context."
        },
    )
    label_max_tokens: int = field(
        default=6,
        metadata={
            "description": "Maximum number of words kept from inferred label context to avoid long/noisy labels."
        },
    )
    require_pdf_extension: bool = field(
        default=True,
        metadata={
            "description": "If True, reject non-.pdf paths before parsing; if False, attempt parsing any file path with PdfReader."
        },
    )

    def _on_install(self, agent: Agent = None):
        """Install and validate buffer/output schema requirements."""
        BufferNode._on_install(self, agent)
        if not isinstance(self._buffer, DictBuffer):
            raise NodeException("Only DictBuffer is supported for " + self.cname())
        if len(self.output_keys) != 4:
            raise NodeException(
                f"{self.cname()} requires exactly 4 output_keys, got {len(self.output_keys)}"
            )

    def _on_execute(self):
        """Read parent-provided PDF paths, extract structured content, and push one row per PDF."""
        file_paths = self._extract_paths_from_parent_data(self.get_parent_data())
        if len(file_paths) == 0:
            raise NodeException("No PDF file paths were found in parent buffer data")

        for file_path in file_paths:
            if not FileUtils.exists_file(file_path):
                raise NodeException("filepath " + file_path + " does not exist")
            if self.require_pdf_extension and not file_path.lower().endswith(".pdf"):
                raise NodeException("filepath " + file_path + " is not a PDF file")

            pdf_result = self._read_pdf(file_path)
            row = dict(
                zip(
                    self.output_keys,
                    [
                        file_path,
                        pdf_result["metadata"],
                        pdf_result["fields"],
                        pdf_result["full_text_content"],
                    ],
                )
            )
            # Push one row batch to preserve list-valued cells like `fields`.
            self.add_data({key: [value] for key, value in row.items()})

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
        """Merge AcroForm field dictionaries with widget annotations into normalized field records."""
        field_map: dict[str, dict] = {}

        form_fields = reader.get_fields() or {}
        for field_name, field_data in form_fields.items():
            normalized_name = str(field_name)
            field_map[normalized_name] = {
                "field_id": normalized_name,
                "field_type": self._to_serializable(self._get_value(field_data, "/FT")) or "",
                "label_context": self._to_serializable(self._get_value(field_data, "/TU")) or "",
                "current_value": self._to_serializable(self._get_value(field_data, "/V")) or "",
                "rect": self._normalize_rect(self._get_value(field_data, "/Rect")),
            }

        for page_idx, page in enumerate(reader.pages):
            spans = spans_by_page[page_idx] if page_idx < len(spans_by_page) else []
            annots = self._get_value(page, "/Annots")
            if not annots:
                continue

            for annot_ref in annots:
                annot = self._resolve_pdf_object(annot_ref)
                if str(self._get_value(annot, "/Subtype")) != "/Widget":
                    continue

                parent = self._resolve_pdf_object(self._get_value(annot, "/Parent"))
                field_id = self._coalesce(
                    self._to_serializable(self._get_value(annot, "/T")),
                    self._to_serializable(self._get_value(parent, "/T")),
                )
                if field_id is None:
                    field_id = f"field_{page_idx}_{len(field_map)}"

                field_id = str(field_id)
                rect = self._normalize_rect(
                    self._coalesce(
                        self._get_value(annot, "/Rect"),
                        self._get_value(parent, "/Rect"),
                    )
                )
                fallback_label = self._coalesce(
                    self._to_serializable(self._get_value(annot, "/TU")),
                    self._to_serializable(self._get_value(parent, "/TU")),
                )

                existing = field_map.get(
                    field_id,
                    {
                        "field_id": field_id,
                        "field_type": "",
                        "label_context": "",
                        "current_value": "",
                        "rect": None,
                    },
                )

                inferred_label = (
                    fallback_label if fallback_label is not None else self._infer_label_context(rect, spans)
                )
                merged = {
                    "field_id": field_id,
                    "field_type": self._coalesce(
                        existing.get("field_type"),
                        self._to_serializable(self._get_value(annot, "/FT")),
                        self._to_serializable(self._get_value(parent, "/FT")),
                        "",
                    ),
                    "label_context": self._coalesce(
                        existing.get("label_context"),
                        inferred_label,
                        "",
                    ),
                    "current_value": self._coalesce(
                        existing.get("current_value"),
                        self._to_serializable(self._get_value(annot, "/V")),
                        self._to_serializable(self._get_value(parent, "/V")),
                        "",
                    ),
                    "rect": existing.get("rect") if existing.get("rect") is not None else rect,
                }
                field_map[field_id] = merged

        return list(field_map.values())

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
            except Exception as e:
                logger.error(e)
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
            except Exception as e:
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
