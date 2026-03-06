from __future__ import annotations

import re
import unicodedata
from typing import Any

from ..NodeException import NodeException


def import_fitz():
    """Import and return the fitz module (PyMuPDF)."""
    try:
        import fitz  # type: ignore

        return fitz
    except Exception as exc:
        raise NodeException("PyMuPDF (fitz) is required. Please install it: pip install PyMuPDF") from exc


def clean_text(text: str) -> str:
    """Collapse whitespace in a string to single spaces."""
    return " ".join(str(text).split())


def classify_widget_type(widget: Any, fitz: Any) -> str:
    """Categorize a PyMuPDF widget into a simplified type string."""
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
        if is_push_button(widget):
            return "unknown"
        return "checkbox"
    return "unknown"


def is_push_button(widget: Any) -> bool:
    """Check if a widget is a push button based on its flags."""
    try:
        flags = int(getattr(widget, "field_flags", 0) or 0)
    except Exception:
        flags = 0
    return (flags & 65536) != 0


def collect_button_states(widget: Any) -> list[str]:
    """Extract and normalize all possible states for a button-like widget."""
    states: list[str] = []

    button_states_obj = getattr(widget, "button_states", None)
    if button_states_obj is not None:
        try:
            raw_button_states = button_states_obj() if callable(button_states_obj) else button_states_obj
            states.extend(flatten_state_values(raw_button_states))
        except Exception:
            pass

    on_state_obj = getattr(widget, "on_state", None)
    if on_state_obj is not None:
        try:
            on_state = on_state_obj() if callable(on_state_obj) else on_state_obj
            if on_state is not None:
                states.append(str(on_state))
        except Exception:
            pass

    normalized: list[str] = []
    seen: set[str] = set()
    for state in states:
        cleaned = normalize_state_name(state)
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


def flatten_state_values(raw: Any) -> list[str]:
    """Recursively flatten a nested structure of state values into a list of strings."""
    if raw is None:
        return []
    if isinstance(raw, dict):
        flat: list[str] = []
        for value in raw.values():
            flat.extend(flatten_state_values(value))
        return flat
    if isinstance(raw, (list, tuple, set)):
        flat = []
        for value in raw:
            flat.extend(flatten_state_values(value))
        return flat
    return [str(raw)]


def normalize_state_name(value: Any) -> str:
    """Clean a button state name by removing leading slashes and extra whitespace."""
    text = clean_text(str(value))
    if text.startswith("/"):
        text = text[1:]
    return text


def ascii_fold(text: str) -> str:
    """Perform simple ASCII folding for German characters."""
    folded = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    folded = folded.replace("Ä", "ae").replace("Ö", "oe").replace("Ü", "ue")
    return folded


def canonicalize_field_key(value: Any) -> str:
    """Create a canonical, alphanumeric-only key from a string for lookups."""
    text = clean_text(str(value)).lower()
    text = ascii_fold(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in text if ch.isalnum())
