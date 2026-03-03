import os
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


def test_write_pdf_form_writes_text_fields_from_json_mapping():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_TEXT")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_TEXT")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"DAK","az-persnr":"12345"}']})
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
    def _fake_import_fitz(self):
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

    monkeypatch.setattr(PDFWriteFormAction, "_import_fitz", _fake_import_fitz)
    monkeypatch.setattr(PDFWriteFormAction, "_index_widgets", _fake_index_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_write_field_to_widgets", _fake_write_field_to_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_save_document", _fake_save_document)

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_WRAP_ERR")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_WRAP_ERR")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"DAK"}']})
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
    def _fake_import_fitz(self):
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

    monkeypatch.setattr(PDFWriteFormAction, "_import_fitz", _fake_import_fitz)
    monkeypatch.setattr(PDFWriteFormAction, "_index_widgets", _fake_index_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_write_field_to_widgets", _fake_write_field_to_widgets)
    monkeypatch.setattr(PDFWriteFormAction, "_save_document", _fake_save_document)

    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_NON_STRICT")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_NON_STRICT")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"DAK","__unknown__":"X"}']})
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
    payload_buf.push({"answer": ['{"kasse":"DAK"}']})
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


def test_write_pdf_form_writes_checkbox_and_radio_states():
    path_buf = ListBuffer(id="B_PDFWRITE_PATHS_BTN")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDFWRITE_PAYLOAD_BTN")
    payload_buf.install()
    payload_buf.push({"answer": ['{"versorgungsbezuege": true, "dienstverh":"nein"}']})
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
    payload_buf.push({"answer": ['{"__unknown_field__":"value"}']})
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
            "answer": ['{"kasse":"AOK"}', '{"az-persnr":"777"}'],
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

    writer = PDFWriteFormAction(
        path_input_keys=["filepath"],
        fill_input_keys=["fields"],
        row_mode="per_pdf",
        output_folder=_output_folder(),
        output_suffix="_ut_roundtrip_"# + uuid.uuid4().hex[:8],
    )
    writer.add_parent(reader)
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


def test_normalize_payload_accepts_selected_state_and_selected_option_aliases():
    writer = PDFWriteFormAction()

    normalized_list = writer._normalize_payload(
        [
            {"write_target_field_id": "dienstverh", "selected_state": "nein"},
            {"field_name": "versorgungsbezuege", "selected_option": "Ja"},
        ]
    )
    assert normalized_list == {"dienstverh": "nein", "versorgungsbezuege": "Ja"}

    normalized_mapping = writer._normalize_payload(
        {
            "dienstverh": {"selected_state": "nein"},
            "versorgungsbezuege": {"selected_option": "Ja"},
        }
    )
    assert normalized_mapping == {"dienstverh": "nein", "versorgungsbezuege": "Ja"}


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
    assert writer._normalize_state_name(widget_no.field_value).lower() == "nein"
    assert writer._normalize_state_name(widget_yes.field_value).lower() == "off"
    assert widget_no.update_calls == 1
    assert widget_yes.update_calls == 1
