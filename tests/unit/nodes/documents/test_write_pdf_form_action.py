import json
import os
import re
import sys
import types
import uuid

import pytest

#pytest.importorskip("fitz")

from pypdf import PdfReader

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

from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction
from pydag.nodes.documents.PDFWriteFormAction import PDFWriteFormAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.services.llm.RAGService import RAGService
from pydag.utils.PDFUtils import normalize_state_name


def _test_pdf_file() -> str:
    return os.path.join(os.path.dirname(__file__), "test_pdf_form", "test_5031.pdf")


def _output_folder() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "resources", "outputs")
    )


def _link_buffer(buffer):
    lba = LinkBufferAction()
    lba.set_buffer(buffer)
    lba.install()
    return lba


def _normalize_pdf_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="ignore")
    else:
        text = str(value)
    text = text.strip()
    if text.startswith("/"):
        text = text[1:]
    if text.lower() == "off":
        return ""
    return text


def _normalized_pdf_field_values(pdf_path: str) -> dict[str, str]:
    reader = PdfReader(pdf_path)
    fields = reader.get_fields() or {}
    return {str(key): _normalize_pdf_value(value.get("/V") if isinstance(value, dict) else None) for key, value in fields.items()}


def _normalize_pdf_name(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.startswith("/"):
        text = text[1:]
    if text.lower() == "off":
        return "Off"
    return text


def _raw_field_value(pdf_path: str, field_name: str) -> str:
    reader = PdfReader(pdf_path)
    fields = reader.get_fields() or {}
    payload = fields.get(field_name)
    if not isinstance(payload, dict):
        return ""
    return _normalize_pdf_name(payload.get("/V"))


def _widget_appearance_states(pdf_path: str, field_name: str) -> list[str]:
    reader = PdfReader(pdf_path)
    states: list[str] = []
    for page in reader.pages:
        annotations = page.get("/Annots") or []
        for annotation_ref in annotations:
            annotation = annotation_ref.get_object()
            if str(annotation.get("/Subtype")) != "/Widget":
                continue
            parent_ref = annotation.get("/Parent")
            parent = parent_ref.get_object() if parent_ref is not None else None
            name = None
            if parent is not None:
                name = parent.get("/T")
            if name is None:
                name = annotation.get("/T")
            if str(name) != field_name:
                continue
            states.append(_normalize_pdf_name(annotation.get("/AS")))
    return states


def _require_fitz_for_pdf_form_tests():
    try:
        import fitz  # type: ignore  # noqa: F401
    except Exception as exc:
        raise AssertionError("PyMuPDF (fitz) is required for PDF checkbox write-state tests") from exc


def test_write_pdf_form_writes_text_fields_from_json_mapping():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_TEXT")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_TEXT")
    payload_buf.install()
    payload_buf.push(
        {
            "answer": [
                '{"field_updates":[{"internal_field_id":"kasse","value":"DAK"},'
                '{"internal_field_id":"az-persnr","value":"12345"}]}'
            ]
        }
    )
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_text_" #+ uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()
    writer.execute()

    data = writer.get_buffer().data()
    assert len(data["output_filepath"]) == 1
    assert data["written_field_count"][0] == 2
    output_file = data["output_filepath"][0]
    assert os.path.isfile(output_file)

    values = _normalized_pdf_field_values(output_file)
    assert values["kasse"] == "DAK"
    assert values["az-persnr"] == "12345"


def test_write_pdf_form_wraps_widget_update_runtime_error_as_node_exception(monkeypatch):
    def _fake_import_fitz():
        class _FakeDocument:
            def close(self):
                return

        class _FakeFitz:
            @staticmethod
            def open(_path):
                return _FakeDocument()

        return _FakeFitz()

    def _fake_index_widgets(self, _document):
        return {"kasse": [object()]}, []

    def _fake_write_field_to_widgets(self, _field_name, _widgets, _value, _fitz):
        raise RuntimeError("Annot is not bound to a page")

    def _fake_save_document(self, _document, _source_path, _output_path):
        return

    monkeypatch.setattr("pydag.nodes.documents.PDFWriteFormAction._pdf_utils.import_fitz", _fake_import_fitz)
    monkeypatch.setattr(PDFWriteFormAction, "_index_widgets", _fake_index_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_write_field_to_widgets", _fake_write_field_to_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_save_document", _fake_save_document)

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_WRAP_ERR")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_WRAP_ERR")
    payload_buf.install()
    payload_buf.push({"answer": ['{"field_updates":[{"internal_field_id":"kasse","value":"DAK"}]}']})
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_wrap_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    with pytest.raises(NodeException, match="could not write pdf file"):
        writer.execute()


def test_write_pdf_form_non_strict_unknown_fields_ignores_extras(monkeypatch):
    def _fake_import_fitz():
        class _FakeDocument:
            def close(self):
                return

        class _FakeFitz:
            @staticmethod
            def open(_path):
                return _FakeDocument()

        return _FakeFitz()

    def _fake_index_widgets(self, _document):
        return {"kasse": [object()]}, []

    def _fake_write_field_to_widgets(self, _field_name, _widgets, value, _fitz):
        return value

    def _fake_save_document(self, _document, _source_path, _output_path):
        return

    monkeypatch.setattr("pydag.nodes.documents.PDFWriteFormAction._pdf_utils.import_fitz", _fake_import_fitz)
    monkeypatch.setattr(PDFWriteFormAction, "_index_widgets", _fake_index_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_write_field_to_widgets", _fake_write_field_to_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_save_document", _fake_save_document)

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_NON_STRICT")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_NON_STRICT")
    payload_buf.install()
    payload_buf.push(
        {
            "answer": [
                '{"field_updates":[{"internal_field_id":"kasse","value":"DAK"},'
                '{"internal_field_id":"__unknown__","value":"X"}]}'
            ]
        }
    )
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_nonstrict_",# + uuid.uuid4().hex[:8],
        strict_unknown_fields=False,
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()
    writer.execute()

    data = writer.get_buffer().data()
    assert data["written_field_count"][0] == 1


def test_write_pdf_form_rejects_non_pdf_input_when_extension_required(tmp_path):
    non_pdf_file = tmp_path / "not_a_pdf.txt"
    non_pdf_file.write_text("not a pdf", encoding="utf-8")

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_NONPDF")
    path_buf.install()
    path_buf.push(str(non_pdf_file))
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_NONPDF")
    payload_buf.install()
    payload_buf.push({"answer": ['{"field_updates":[{"internal_field_id":"kasse","value":"DAK"}]}']})
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_nonpdf_",# + uuid.uuid4().hex[:8],
        require_pdf_extension=True,
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    with pytest.raises(NodeException):
        writer.execute()


def test_write_pdf_form_install_rejects_duplicate_fill_input_keys():
    writer = PDFWriteFormAction(fill_input_keys=["answer", "answer"])
    with pytest.raises(NodeException, match="fill_input_keys must contain unique entries"):
        writer.install()


def test_write_pdf_form_install_rejects_duplicate_output_keys():
    writer = PDFWriteFormAction(output_keys=["filepath", "filepath", "written_fields", "written_field_count"])
    with pytest.raises(NodeException, match="output_keys must contain unique entries"):
        writer.install()


def test_write_pdf_form_rejects_output_path_that_matches_source_pdf():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_SAME_OUT")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_SAME_OUT")
    payload_buf.install()
    payload_buf.push({"answer": ['{"field_updates":[{"internal_field_id":"kasse","value":"DAK"}]}']})
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=None,
        output_suffix="",
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    with pytest.raises(NodeException, match="output path resolves to the source PDF"):
        writer.execute()


def test_write_pdf_form_rejects_non_mapping_field_values_after_resolution(monkeypatch):
    pdf_file = _test_pdf_file()

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_BAD_PAYLOAD")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_BAD_PAYLOAD")
    payload_buf.install()
    payload_buf.push({"answer": ['{"field_updates":[{"internal_field_id":"kasse","value":"DAK"}]}']})
    payload_parent = _link_buffer(payload_buf)

    monkeypatch.setattr(PDFWriteFormAction, "_extract_payloads_by_path", lambda self, _data: {pdf_file: ["bad"]})
    monkeypatch.setattr(PDFWriteFormAction, "_extract_fill_payloads", lambda self, _data: [])

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_bad_payload_",
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    with pytest.raises(NodeException, match="field_values must be a mapping"):
        writer.execute()


def test_write_pdf_form_writes_checkbox_and_radio_states():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_BTN")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_BTN")
    payload_buf.install()
    payload_buf.push(
        {
            "answer": [
                '{"field_updates":[{"internal_field_id":"versorgungsbezuege","selected_state":true},'
                '{"internal_field_id":"dienstverh","selected_state":"nein"}]}'
            ]
        }
    )
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_btn_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()
    writer.execute()

    output_file = writer.get_buffer().data()["output_filepath"][0]
    values = _normalized_pdf_field_values(output_file)
    assert values["versorgungsbezuege"].lower() == "ja"
    assert values["dienstverh"].lower() == "nein"


def test_write_pdf_form_fails_fast_for_unknown_fields_by_default():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_UNKNOWN")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_UNKNOWN")
    payload_buf.install()
    payload_buf.push({"answer": ['{"field_updates":[{"internal_field_id":"__unknown_field__","value":"value"}]}']})
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_unknown_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    with pytest.raises(NodeException):
        writer.execute()


def test_write_pdf_form_per_field_mode_auto_merges_rows_by_filepath():
    pdf_file = _test_pdf_file()

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_PERFIELD")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_PERFIELD")
    payload_buf.install()
    payload_buf.push(
        {
            "filepath": [pdf_file, pdf_file],
            "answer": [
                '{"field_updates":[{"internal_field_id":"kasse","value":"AOK"}]}',
                '{"field_updates":[{"internal_field_id":"az-persnr","value":"777"}]}',
            ],
        }
    )
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        row_mode="per_field",
        path_input_keys=["values", "filepath"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_perfield_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()
    writer.execute()

    data = writer.get_buffer().data()
    assert len(data["filepath"]) == 1
    assert data["written_field_count"][0] == 2
    output_file = data["output_filepath"][0]

    values = _normalized_pdf_field_values(output_file)
    assert values["kasse"] == "AOK"
    assert values["az-persnr"] == "777"


def test_roundtrip_read_to_write_preserves_field_values():
    pdf_file = _test_pdf_file()

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_ROUNDTRIP")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    reader = PDFReadFormAction(
        input_keys=["values"],
        row_mode="per_pdf",
        include_bridge_prompt=False,
    )
    reader.add_parent(path_parent)
    reader.install()
    reader.execute()

    read_fields = reader.get_buffer().data()["fields"][0]
    updates: list[dict[str, object]] = []
    for field in read_fields:
        update: dict[str, object] = {
            "internal_field_id": str(
                field.get("internal_field_id", field.get("write_target_field_id", field.get("field_name", "")))
            ),
        }
        if str(field.get("field_type", "")) in {"checkbox", "radio"}:
            update["selected_state"] = field.get("field_value", "")
        else:
            update["value"] = field.get("field_value", "")
        updates.append(update)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_ROUNDTRIP")
    payload_buf.install()
    payload_buf.push({"answer": [json.dumps({"field_updates": updates}, ensure_ascii=True)]})
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_roundtrip_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()
    writer.execute()

    output_file = writer.get_buffer().data()["output_filepath"][0]
    source_values = _normalized_pdf_field_values(pdf_file)
    output_values = _normalized_pdf_field_values(output_file)
    assert source_values == output_values


def test_resolve_target_button_state_exact_and_normalized_matches():
    writer = PDFWriteFormAction()
    available_states = ["Ja", "Off"]

    assert writer._resolve_target_button_state("ja", available_states) == "Ja"
    assert writer._resolve_target_button_state("/ Ja ", available_states) == "Ja"


def test_resolve_target_button_state_semantic_binary_values():
    writer = PDFWriteFormAction()
    available_states = ["Ja", "Off"]

    assert writer._resolve_target_button_state("yes", available_states) == "Ja"
    assert writer._resolve_target_button_state("y", available_states) == "Ja"
    assert writer._resolve_target_button_state("checked", available_states) == "Ja"
    assert writer._resolve_target_button_state("ja", available_states) == "Ja"
    assert writer._resolve_target_button_state(True, available_states) == "Ja"
    assert writer._resolve_target_button_state(1, available_states) == "Ja"

    assert writer._resolve_target_button_state("no", available_states) == "Off"
    assert writer._resolve_target_button_state("n", available_states) == "Off"
    assert writer._resolve_target_button_state("unchecked", available_states) == "Off"
    assert writer._resolve_target_button_state("nein", available_states) == "Off"
    assert writer._resolve_target_button_state(False, available_states) == "Off"
    assert writer._resolve_target_button_state(0, available_states) == "Off"


def test_resolve_target_button_state_binary_fallback_success_for_unknown_token():
    writer = PDFWriteFormAction()
    available_states = ["CustomOn", "Off"]
    assert writer._resolve_target_button_state("something-unmapped", available_states) == "CustomOn"


def test_resolve_target_button_state_non_binary_raises_ambiguity_with_states():
    writer = PDFWriteFormAction()
    available_states = ["Ja", "nein", "Off"]

    with pytest.raises(NodeException, match="Available states"):
        writer._resolve_target_button_state("true", available_states)


def test_normalize_payload_strict_field_updates_contract():
    writer = PDFWriteFormAction()

    normalized_list = writer._normalize_payload(
        [
            {"internal_field_id": "dienstverh", "selected_state": "nein"},
            {"internal_field_id": "versorgungsbezuege", "selected_state": "Ja"},
        ]
    )
    assert normalized_list == {"dienstverh": "nein", "versorgungsbezuege": "Ja"}

    normalized_mapping = writer._normalize_payload(
        {
            "field_updates": [
                {"internal_field_id": "dienstverh", "selected_state": "nein"},
                {"internal_field_id": "versorgungsbezuege", "selected_state": "Ja"},
            ]
        }
    )
    assert normalized_mapping == {"dienstverh": "nein", "versorgungsbezuege": "Ja"}

    with pytest.raises(NodeException, match="Invalid fill payload object"):
        writer._normalize_payload({"dienstverh": {"selected_state": "nein"}})


def test_write_button_group_integration_applies_expected_widget_states():
    class _FakeButtonWidget:
        def __init__(self, states):
            self._states = states
            self.field_value = None
            self.update_calls = 0

        def button_states(self):
            return self._states

        def on_state(self):
            for raw_state in self._states:
                state = str(raw_state)
                if state.startswith("/"):
                    state = state[1:]
                if state.lower() != "off":
                    return raw_state
            return None

        def update(self):
            self.update_calls += 1

    writer = PDFWriteFormAction()
    widget_no = _FakeButtonWidget(["/nein", "/Off"])
    widget_yes = _FakeButtonWidget(["/Ja", "/Off"])

    applied_state = writer._write_button_group([widget_no, widget_yes], "nein")
    assert applied_state.lower() == "nein"
    assert normalize_state_name(widget_no.field_value).lower() == "nein"
    assert normalize_state_name(widget_yes.field_value).lower() == "off"
    assert widget_no.update_calls == 1
    assert widget_yes.update_calls == 1


def test_write_pdf_form_checkbox_off_to_on_updates_field_and_widget_state():
    _require_fitz_for_pdf_form_tests()
    target_field = "Kontrollk\u00e4stchen2"
    opposite_field = "Kontrollk\u00e4stchen1"

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_CHECKBOX_ON")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_CHECKBOX_ON_STRICT")
    payload_buf.install()
    payload_buf.push(
        {"answer": ['{"field_updates":[{"internal_field_id":"Kontrollk\\u00e4stchen2","selected_state":true}]}']}
    )
    payload_parent = _link_buffer(payload_buf)

    writer = PDFWriteFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_output_folder(),
        output_suffix="_ut_checkbox_on_yes_",
    )
    writer.add_parent(path_parent)
    writer.add_parent(payload_parent)
    writer.install()

    source_field_state = _raw_field_value(_test_pdf_file(), target_field)
    source_widget_states = _widget_appearance_states(_test_pdf_file(), target_field)
    assert source_field_state in {"", "Off"}
    assert len(source_widget_states) > 0
    assert all(state in {"", "Off"} for state in source_widget_states)

    writer.execute()
    output_file = writer.get_buffer().data()["output_filepath"][0]

    output_field_state = _raw_field_value(output_file, target_field)
    output_widget_states = _widget_appearance_states(output_file, target_field)
    assert output_field_state.lower() == "ja"
    assert any(state.lower() == "ja" for state in output_widget_states)

    # Ensure the opposite option in this pair does not become checked.
    opposite_output_state = _raw_field_value(output_file, opposite_field)
    assert opposite_output_state in {"", "Off"}


class _DeterministicQuestionRAGService(RAGService):
    """Minimal test double that answers atomic field questions deterministically."""

    def _on_start(self):
        return

    def _on_stop(self):
        return

    def chat(
        self,
        question: str,
        instruction: str | None = None,
        input_context: str | dict | list | None = None,
        retrieval_query: str | None = None,
        use_rag_context: bool = True,
        session_id: str = "DEFAULT_SESSION",
    ) -> str:
        prompt = str(question)
        id_match = re.search(r'internal_field_id="([^"]+)"', prompt)
        type_match = re.search(r'type="([^"]+)"', prompt)
        internal_field_id = id_match.group(1) if id_match is not None else ""
        field_type = type_match.group(1) if type_match is not None else ""

        if internal_field_id == "kasse":
            payload = {"field_updates": [{"internal_field_id": internal_field_id, "value": "DAK"}]}
            return json.dumps(payload, ensure_ascii=True)
        if internal_field_id == "Kontrollkästchen2":
            payload = {"field_updates": [{"internal_field_id": internal_field_id, "selected_state": "Ja"}]}
            return json.dumps(payload, ensure_ascii=True)

        if field_type in {"checkbox", "radio"}:
            payload = {"field_updates": [{"internal_field_id": internal_field_id, "selected_state": "Off"}]}
            return json.dumps(payload, ensure_ascii=True)

        payload = {"field_updates": [{"internal_field_id": internal_field_id, "value": ""}]}
        return json.dumps(payload, ensure_ascii=True)


@pytest.mark.skip(reason="Test uses LLM")
def test_question_based_pipeline_read_llm_write_maps_answers_by_internal_field_id():
    _require_fitz_for_pdf_form_tests()

    path_buf = ListBuffer(id="B_Q_PIPE_PATHS")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    reader = PDFReadFormAction(
        id="READ_Q_PIPE",
        input_keys=["values"],
        row_mode="per_field",
        include_bridge_prompt=True,
    )
    reader.add_parent(path_parent)
    reader.install()
    reader.execute()

    read_data = reader.get_buffer().data()
    rows = list(zip(read_data.get("filepath", []), read_data.get("fields", []), read_data.get("llm_prompt", [])))
    selected_rows: list[tuple[str, str]] = []
    target_checkbox = "Kontrollkästchen2"

    for filepath, fields, prompt in rows:
        if len(fields) != 1:
            continue
        field = fields[0]
        internal_field_id = str(field.get("internal_field_id", "")).strip()
        if internal_field_id == "kasse":
            selected_rows.append((str(filepath), str(prompt)))
            continue
        if internal_field_id != target_checkbox:
            continue
        option_text = str(field.get("option_text", "")).lower()
        if "ja" not in option_text:
            continue
        selected_rows.append((str(filepath), str(prompt)))

    assert len(selected_rows) == 2

    llm_input_buf = DictBuffer(id="B_Q_PIPE_LLM_INPUT")
    llm_input_buf.install()
    llm_input_buf.push(
        {
            "filepath": [item[0] for item in selected_rows],
            "llm_prompt": [item[1] for item in selected_rows],
        }
    )
    llm_parent = _link_buffer(llm_input_buf)

    service = _DeterministicQuestionRAGService(
        id="RAG_Q_PIPE_FAKE",
        model_provider="OPENAI",
        model="gpt-4.1-mini",
        retain_messages=False,
    )
    service.install()
    service.start()
    try:
        llm_action = LLMChatAction(
            id="LLM_Q_PIPE",
            question_key="llm_prompt",
            instruction_value=(
                "Return only JSON object without markdown. "
                "Return exactly one top-level key field_updates."
            ),
            use_rag_context=False,
            pass_through_keys=["filepath"],
        )
        llm_action.add_parent(llm_parent)
        llm_action.set_service(service)
        llm_action.install()
        llm_action.execute()

        writer = PDFWriteFormAction(
            id="WRITE_Q_PIPE",
            path_input_keys=["filepath"],
            fill_input_keys=["answer"],
            row_mode="per_field",
            output_folder=_output_folder(),
            output_suffix="_ut_q_pipeline_",
        )
        writer.add_parent(llm_action)
        writer.install()
        writer.execute()

        out_data = writer.get_buffer().data()
        assert len(out_data.get("output_filepath", [])) == 1
        output_file = str(out_data["output_filepath"][0])
        assert os.path.isfile(output_file)

        values = _normalized_pdf_field_values(output_file)
        assert values["kasse"] == "DAK"

        checkbox_state = _raw_field_value(output_file, target_checkbox)
        widget_states = _widget_appearance_states(output_file, target_checkbox)
        assert checkbox_state.lower() == "ja"
        assert any(str(state).lower() == "ja" for state in widget_states)
    finally:
        service.stop()
