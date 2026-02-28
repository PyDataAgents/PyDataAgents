import os
import sys
import types
import uuid

import pytest

pytest.importorskip("fitz")

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
    return os.path.join("resources", "Outputs")


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
        output_suffix="_ut_text_" + uuid.uuid4().hex[:8],
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
        output_suffix="_ut_btn_" + uuid.uuid4().hex[:8],
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
        output_suffix="_ut_unknown_" + uuid.uuid4().hex[:8],
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
        output_suffix="_ut_perfield_" + uuid.uuid4().hex[:8],
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
        output_suffix="_ut_roundtrip_" + uuid.uuid4().hex[:8],
    )
    writer.add_parent(reader)
    writer.install()
    writer.execute()

    output_file = writer.get_buffer().data()["output_filepath"][0]
    source_values = _normalized_pdf_field_values(pdf_file)
    output_values = _normalized_pdf_field_values(output_file)
    assert source_values == output_values
