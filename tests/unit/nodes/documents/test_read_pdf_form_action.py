import os
import sys
import types

import pytest

#pytest.importorskip("fitz")

# Fallback for environments where graphviz is not installed.
if "graphviz" not in sys.modules:
    graphviz_stub = types.ModuleType("graphviz")

    class _DummyDigraph:
        def __init__(self, *args, **kwargs):
            return

        def node(self, *args, **kwargs):
            return

        def edge(self, *args, **kwargs):
            return

        def render(self, *args, **kwargs):
            return ""

    graphviz_stub.Digraph = _DummyDigraph
    sys.modules["graphviz"] = graphviz_stub

from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction, generate_llm_prompt


def _test_pdf_file() -> str:
    return os.path.join(os.path.dirname(__file__), "test_pdf_form", "test_5031.pdf")


def _link_buffer(buffer):
    lba = LinkBufferAction()
    lba.set_buffer(buffer)
    lba.install()
    return lba


def _run_read(row_mode: str = "per_pdf", include_bridge_prompt: bool = True):
    path_buffer = ListBuffer(id="B_PDFREAD_PATHS")
    path_buffer.install()
    path_buffer.push(_test_pdf_file())

    path_parent = _link_buffer(path_buffer)
    reader = PDFReadFormAction(
        input_keys=["values"],
        row_mode=row_mode,
        include_bridge_prompt=include_bridge_prompt,
    )
    reader.add_parent(path_parent)
    reader.install()
    reader.execute()
    return reader.get_buffer().data()


def test_read_pdf_form_default_per_pdf_extracts_context_and_prompt():
    data = _run_read(row_mode="per_pdf", include_bridge_prompt=True)

    assert "filepath" in data
    assert "metadata" in data
    assert "fields" in data
    assert "full_text_content" in data
    assert "llm_prompt" in data

    assert len(data["filepath"]) == 1
    assert data["filepath"][0].endswith("test_5031.pdf")
    assert len(data["metadata"]) == 1
    assert int(data["metadata"][0]["pages"]) >= 1
    assert len(data["fields"]) == 1

    fields = data["fields"][0]
    assert isinstance(fields, list)
    assert len(fields) > 0

    required_keys = {
        "field_name",
        "write_target_field_id",
        "field_type",
        "field_value",
        "tooltip",
        "visual_label",
        "page_context",
        "page_index",
        "rect",
        "is_writable",
        "button_states",
    }
    for field in fields:
        assert required_keys.issubset(set(field.keys()))
        assert isinstance(field["field_name"], str)
        assert field["field_name"] != ""
        assert field["write_target_field_id"] == field["field_name"]
        assert isinstance(field["rect"], list)
        assert len(field["rect"]) == 4
        assert isinstance(field["is_writable"], bool)
        assert isinstance(field["button_states"], list)
        if field["field_type"] in {"checkbox", "radio"}:
            assert len(field["button_states"]) > 0
            assert any(str(item).lower() == "off" for item in field["button_states"])

    assert any(str(field["visual_label"]).strip() != "" for field in fields)
    assert any(str(field["page_context"]).strip() != "" for field in fields)

    assert len(data["full_text_content"]) == 1
    assert str(data["full_text_content"][0]).strip() != ""

    prompt = data["llm_prompt"][0]
    assert isinstance(prompt, str)
    assert prompt.strip() != ""
    assert "strict JSON object" in prompt
    assert "field_name" in prompt


def test_read_pdf_form_per_field_emits_one_field_per_row():
    data = _run_read(row_mode="per_field", include_bridge_prompt=True)

    assert "fields" in data
    assert len(data["fields"]) > 0
    assert len(data["filepath"]) == len(data["fields"])
    assert len(data["llm_prompt"]) == len(data["fields"])

    for row_fields, prompt in zip(data["fields"], data["llm_prompt"]):
        assert isinstance(row_fields, list)
        assert len(row_fields) == 1
        field_name = row_fields[0]["field_name"]
        assert field_name in prompt


def test_read_pdf_form_keeps_llm_prompt_column_when_disabled():
    data = _run_read(row_mode="per_pdf", include_bridge_prompt=False)
    assert "llm_prompt" in data
    assert len(data["llm_prompt"]) == 1
    assert data["llm_prompt"][0] == ""


def test_read_pdf_form_raises_for_missing_pdf():
    missing_pdf = os.path.join(os.path.dirname(__file__), "test_pdf_form", "missing_file.pdf")
    path_buffer = ListBuffer(id="B_PDFREAD_MISSING")
    path_buffer.install()
    path_buffer.push(missing_pdf)

    path_parent = _link_buffer(path_buffer)
    reader = PDFReadFormAction(input_keys=["values"])
    reader.add_parent(path_parent)
    reader.install()

    with pytest.raises(NodeException):
        reader.execute()


def test_read_pdf_form_install_raises_for_invalid_row_mode():
    reader = PDFReadFormAction(row_mode="invalid")
    with pytest.raises(NodeException):
        reader.install()


def test_generate_llm_prompt_includes_exact_json_key_template():
    payload = [
        {
            "field_name": "kasse",
            "write_target_field_id": "kasse",
            "field_type": "text",
            "tooltip": "Krankenkasse",
            "visual_label": "Krankenkasse",
            "page_context": "Persoenliche Daten",
            "button_states": [],
        },
        {
            "field_name": "dienstverh",
            "write_target_field_id": "dienstverh",
            "field_type": "radio",
            "tooltip": "Dienstverhaeltnis",
            "visual_label": "Dienstverhaeltnis",
            "page_context": "Persoenliche Daten",
            "button_states": ["nein", "Ja", "Off"],
        },
    ]
    prompt = generate_llm_prompt(payload)
    assert "kasse" in prompt
    assert "dienstverh" in prompt
    assert "write_target_field_id" in prompt
    assert "button_states" in prompt
    assert "<determined_value>" in prompt
    assert "Return JSON only" in prompt
    assert "Do not add keys" in prompt
