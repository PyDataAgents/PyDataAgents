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
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction



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
        "internal_field_id",
        "field_name",
        "answer_key",
        "generated_question",
        "question_context",
        "field_type",
        "field_value",
        "tooltip",
        "visual_label",
        "page_context",
        "option_text",
        "question_text",
        "section_header",
        "context_signature",
        "context_markers",
        "page_index",
        "rect",
        "is_writable",
        "button_states",
    }
    for field in fields:
        assert required_keys.issubset(set(field.keys()))
        assert isinstance(field["internal_field_id"], str)
        assert field["internal_field_id"] != ""
        assert field["field_name"] == field["internal_field_id"]
        assert field["answer_key"] in {"value", "selected_state"}
        assert isinstance(field["generated_question"], str) and str(field["generated_question"]).strip() != ""
        assert isinstance(field["question_context"], str) and str(field["question_context"]).strip() != ""
        assert isinstance(field["rect"], list)
        assert len(field["rect"]) == 4
        assert isinstance(field["is_writable"], bool)
        assert isinstance(field["button_states"], list)
        assert isinstance(field["context_markers"], list)
        if field["field_type"] in {"checkbox", "radio"}:
            assert len(field["button_states"]) > 0
            assert any(str(item).lower() == "off" for item in field["button_states"])
            assert str(field["option_text"]).strip() != ""
            assert str(field["context_signature"]).strip() != ""
            assert field["answer_key"] == "selected_state"
        else:
            assert field["answer_key"] == "value"

    assert any(str(field["visual_label"]).strip() != "" for field in fields)
    assert any(str(field["page_context"]).strip() != "" for field in fields)

    assert len(data["full_text_content"]) == 1
    assert str(data["full_text_content"][0]).strip() != ""

    prompt = data["llm_prompt"][0]
    assert isinstance(prompt, str)
    assert prompt.strip() != ""
    assert '"field_updates"' in prompt
    assert "generated_question" in prompt
    assert "internal_field_id" in prompt
    assert "Do not infer business meaning from internal_field_id alone" in prompt


def test_read_pdf_form_per_field_emits_one_field_per_row():
    data = _run_read(row_mode="per_field", include_bridge_prompt=True)

    assert "fields" in data
    assert len(data["fields"]) > 0
    assert len(data["filepath"]) == len(data["fields"])
    assert len(data["llm_prompt"]) == len(data["fields"])

    for row_fields, prompt in zip(data["fields"], data["llm_prompt"]):
        assert isinstance(row_fields, list)
        assert len(row_fields) == 1
        internal_field_id = row_fields[0]["internal_field_id"]
        generated_question = row_fields[0]["generated_question"]
        assert internal_field_id in prompt
        assert generated_question in prompt


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


def test_read_pdf_form_install_rejects_duplicate_input_keys():
    reader = PDFReadFormAction(input_keys=["values", "values"])
    with pytest.raises(NodeException, match="must contain unique entries"):
        reader.install()


def test_read_pdf_form_install_rejects_duplicate_output_keys():
    reader = PDFReadFormAction(output_keys=["filepath", "metadata", "fields", "fields", "llm_prompt"])
    with pytest.raises(NodeException, match="must contain unique entries"):
        reader.install()


def test_read_pdf_form_wraps_runtime_processing_errors_as_node_exception(monkeypatch):
    def _fake_import_fitz():
        class _FakePage:
            def get_text(self, _mode):
                raise RuntimeError("page text extraction failed")

        class _FakeDocument:
            page_count = 1
            metadata = {}

            def load_page(self, _page_index):
                return _FakePage()

            def close(self):
                return

        class _FakeFitz:
            @staticmethod
            def open(_path):
                return _FakeDocument()

        return _FakeFitz()

    monkeypatch.setattr("pydag.nodes.documents.PDFReadFormAction._pdf_utils.import_fitz", _fake_import_fitz)

    path_buffer = ListBuffer(id="B_PDFREAD_RUNTIME_ERR")
    path_buffer.install()
    path_buffer.push(_test_pdf_file())

    path_parent = _link_buffer(path_buffer)
    reader = PDFReadFormAction(input_keys=["values"])
    reader.add_parent(path_parent)
    reader.install()

    with pytest.raises(NodeException, match="could not read pdf file"):
        reader.execute()


def test_generate_llm_prompt_includes_exact_json_key_template():
    payload = [
        {
            "internal_field_id": "kasse",
            "field_type": "text",
            "generated_question": "What value should be written into Krankenkasse?",
            "question_context": "Persoenliche Daten",
            "button_states": [],
        },
        {
            "internal_field_id": "dienstverh",
            "field_type": "radio",
            "generated_question": "For section Persoenliche Daten, which state should be selected?",
            "question_context": "Persoenliche Daten",
            "button_states": ["nein", "Ja", "Off"],
        },
    ]
    prompt = PDFReadFormAction.generate_llm_prompt(payload)
    assert "kasse" in prompt
    assert "dienstverh" in prompt
    assert "internal_field_id" in prompt
    assert "button_states" in prompt
    assert "generated_question" in prompt
    assert "field_updates" in prompt
    assert "selected_state" in prompt
    assert "Return JSON only" in prompt
    assert "no extra top-level keys" in prompt
