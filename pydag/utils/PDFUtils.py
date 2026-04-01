from __future__ import annotations

import unicodedata
from typing import Any

from ..nodes.NodeException import NodeException


class PDFUtils:
    """Utility helpers shared by PDF form read/write actions."""

    _WIDGET_TYPES = (
        ("PDF_WIDGET_TYPE_TEXT", "text"),
        ("PDF_WIDGET_TYPE_CHECKBOX", "checkbox"),
        ("PDF_WIDGET_TYPE_RADIOBUTTON", "radio"),
        ("PDF_WIDGET_TYPE_COMBOBOX", "dropdown"),
        ("PDF_WIDGET_TYPE_LISTBOX", "listbox"),
        ("PDF_WIDGET_TYPE_SIGNATURE", "signature"),
    )

    @staticmethod
    def import_fitz():
        """Import and return the fitz module (PyMuPDF)."""
        try:
            import fitz  # type: ignore

            return fitz
        except Exception as exc:
            raise NodeException("PyMuPDF (fitz) is required. Please install it: pip install PyMuPDF") from exc

    @staticmethod
    def clean_text(text: Any) -> str:
        """Collapse whitespace in a string to single spaces."""
        return " ".join(str(text).split())

    @staticmethod
    def classify_widget_type(widget: Any, fitz: Any) -> str:
        """Categorize a PyMuPDF widget into a simplified type string."""
        code = getattr(widget, "field_type", None)
        mapping = {getattr(fitz, name, object()): kind for name, kind in PDFUtils._WIDGET_TYPES}
        if code in mapping:
            return mapping[code]

        type_string = str(getattr(widget, "field_type_string", "") or "").lower()
        for token, kind in (
            ("text", "text"),
            ("check", "checkbox"),
            ("radio", "radio"),
            ("combo", "dropdown"),
            ("list", "listbox"),
            ("sign", "signature"),
        ):
            if token in type_string:
                return kind

        if code == getattr(fitz, "PDF_WIDGET_TYPE_BUTTON", object()):
            return "unknown" if PDFUtils.is_push_button(widget) else "checkbox"
        return "unknown"

    @staticmethod
    def is_push_button(widget: Any) -> bool:
        """Check if a widget is a push button based on its flags."""
        try:
            flags = int(getattr(widget, "field_flags", 0) or 0)
        except Exception:
            flags = 0
        return (flags & 65536) != 0

    @staticmethod
    def collect_button_states(widget: Any) -> list[str]:
        """Extract and normalize all possible states for a button-like widget."""
        states: list[str] = []
        for attr in ("button_states", "on_state"):
            value = getattr(widget, attr, None)
            if value is None:
                continue
            try:
                raw = value() if callable(value) else value
            except Exception:
                continue
            if attr == "button_states":
                states.extend(PDFUtils.flatten_state_values(raw))
            elif raw is not None:
                states.append(str(raw))

        normalized: list[str] = []
        seen: set[str] = set()
        for state in states:
            cleaned = PDFUtils.normalize_state_name(state)
            if cleaned == "":
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(cleaned)

        if "off" not in seen:
            normalized.append("Off")
        return normalized

    @staticmethod
    def flatten_state_values(raw: Any) -> list[str]:
        """Recursively flatten a nested structure of state values into a list of strings."""
        if raw is None:
            return []
        if isinstance(raw, dict):
            flat: list[str] = []
            for value in raw.values():
                flat.extend(PDFUtils.flatten_state_values(value))
            return flat
        if isinstance(raw, (list, tuple, set)):
            flat: list[str] = []
            for value in raw:
                flat.extend(PDFUtils.flatten_state_values(value))
            return flat
        return [str(raw)]

    @staticmethod
    def normalize_state_name(value: Any) -> str:
        """Clean a button state name by removing leading slashes and extra whitespace."""
        text = PDFUtils.clean_text(value)
        return text[1:] if text.startswith("/") else text

    @staticmethod
    def ascii_fold(text: str) -> str:
        """Perform simple ASCII folding for German characters."""
        replacements = (
            (bytes.fromhex("c3a4").decode("latin1"), "ae"),
            (bytes.fromhex("c3b6").decode("latin1"), "oe"),
            (bytes.fromhex("c3bc").decode("latin1"), "ue"),
            (bytes.fromhex("c39f").decode("latin1"), "ss"),
            (bytes.fromhex("c384").decode("latin1"), "ae"),
            (bytes.fromhex("c396").decode("latin1"), "oe"),
            (bytes.fromhex("c39c").decode("latin1"), "ue"),
        )
        folded = text
        for source, target in replacements:
            folded = folded.replace(source, target)
        return folded

    @staticmethod
    def canonicalize_field_key(value: Any) -> str:
        """Create a canonical, alphanumeric-only key from a string for lookups."""
        text = PDFUtils.clean_text(value).lower()
        text = PDFUtils.ascii_fold(text)
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        return "".join(ch for ch in text if ch.isalnum())


import_fitz = PDFUtils.import_fitz
clean_text = PDFUtils.clean_text
classify_widget_type = PDFUtils.classify_widget_type
is_push_button = PDFUtils.is_push_button
collect_button_states = PDFUtils.collect_button_states
flatten_state_values = PDFUtils.flatten_state_values
normalize_state_name = PDFUtils.normalize_state_name
ascii_fold = PDFUtils.ascii_fold
canonicalize_field_key = PDFUtils.canonicalize_field_key

__all__ = [
    "PDFUtils",
    "ascii_fold",
    "canonicalize_field_key",
    "classify_widget_type",
    "clean_text",
    "collect_button_states",
    "flatten_state_values",
    "import_fitz",
    "is_push_button",
    "normalize_state_name",
]
