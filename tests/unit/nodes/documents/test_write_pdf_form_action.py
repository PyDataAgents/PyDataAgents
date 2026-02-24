import os
import sys
import types
import json
import random

import pytest
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
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.documents.ReadPDFFormAction import ReadPDFFormAction
from pydag.nodes.documents.WritePDFFormAction import WritePDFFormAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.services.llm.LLMService import LLMService


def _test_pdf_form_folder() -> str:
    return os.path.join(os.path.dirname(__file__), "test_pdf_form")


def _test_output_folder() -> str:
    return os.path.join(_test_pdf_form_folder(), "output")


def _test_pdf_form_file() -> str:
    folder = _test_pdf_form_folder()
    pdfs = sorted(
        [
            os.path.join(folder, name)
            for name in os.listdir(folder)
            if name.lower().endswith(".pdf")
        ]
    )
    if len(pdfs) == 0:
        raise AssertionError("No PDF fixture found in test_pdf_form folder.")
    return pdfs[0]


def _link_buffer(buffer):
    lba = LinkBufferAction()
    lba.set_buffer(buffer)
    lba.install()
    return lba


def _normalized_pdf_field_values(pdf_path: str) -> dict[str, str]:
    reader = PdfReader(pdf_path)
    fields = reader.get_fields() or {}
    values: dict[str, str] = {}
    for field_id, payload in fields.items():
        value = payload.get("/V") if isinstance(payload, dict) else None
        if value is None:
            values[str(field_id)] = ""
        elif isinstance(value, bytes):
            values[str(field_id)] = value.decode("utf-8", errors="ignore")
        else:
            values[str(field_id)] = str(value)
    return values


def test_writes_pdf_form_from_two_parents_with_json_answer_payload(tmp_path):
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    lfa.install()
    lfa.execute()

    payload_buf = DictBuffer(id="B_PDF_FILL_JSON")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"AOK","az-persnr":"12345"}']})
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(lfa)
    wpa.add_parent(payload_parent)
    wpa.install()
    wpa.execute()

    data = wpa.get_buffer().data()
    assert "filepath" in data
    assert "output_filepath" in data
    assert "written_fields" in data
    assert "written_field_count" in data
    assert len(data["filepath"]) == 1
    assert data["written_field_count"][0] == 2

    out_file = data["output_filepath"][0]
    assert os.path.isfile(out_file)
    assert out_file.endswith("_filled.pdf")

    reader = PdfReader(out_file)
    fields = reader.get_fields() or {}
    assert fields["kasse"]["/V"] == "AOK"
    assert fields["az-persnr"]["/V"] == "12345"


def test_writes_pdf_form_from_read_style_fields_payload(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_PDF_PATHS")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    field_list = [
        {"field_id": "kasse", "current_value": "BKK"},
        {"field_id": "az-persnr", "current_value": "4711"},
    ]
    payload_buf = DictBuffer(id="B_PDF_FIELDS")
    payload_buf.install()
    payload_buf.push({"fields": [field_list]})
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["fields"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(payload_parent)
    wpa.install()
    wpa.execute()

    out_file = wpa.get_buffer().data()["output_filepath"][0]
    reader = PdfReader(out_file)
    fields = reader.get_fields() or {}

    assert fields["kasse"]["/V"] == "BKK"
    assert fields["az-persnr"]["/V"] == "4711"


def test_execute_raises_if_two_parents_are_required_but_missing():
    wpa = WritePDFFormAction(require_two_parents=True)
    wpa.install()
    with pytest.raises(NodeException):
        wpa.execute()


def test_execute_raises_for_mismatched_payload_count(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_PDF_PATHS_MISMATCH")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDF_FILL_MISMATCH")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"AOK"}', '{"kasse":"TK"}']})
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(payload_parent)
    wpa.install()

    with pytest.raises(NodeException):
        wpa.execute()


def test_custom_output_keys_are_used(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_PDF_PATHS_CUSTOM")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDF_FILL_CUSTOM")
    payload_buf.install()
    payload_buf.push({"answer": ['{"kasse":"DAK"}']})
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_keys=["source", "target", "fields_written", "count"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(payload_parent)
    wpa.install()
    wpa.execute()

    data = wpa.get_buffer().data()
    assert "source" in data
    assert "target" in data
    assert "fields_written" in data
    assert "count" in data
    assert "filepath" not in data
    assert "output_filepath" not in data


def test_execute_raises_when_values_is_used_for_paths_and_fill_payloads(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_VALUES_PATH")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    fill_buf = ListBuffer(id="B_VALUES_FILL")
    fill_buf.install()
    fill_buf.push('{"kasse":"AOK","az-persnr":"12345"}')
    fill_parent = _link_buffer(fill_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["values"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(fill_parent)
    wpa.install()

    with pytest.raises(NodeException):
        wpa.execute()


def test_merges_multiple_payload_rows_for_same_filepath(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_PDF_PATHS_MERGE_BY_PATH")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDF_FILL_MERGE_BY_PATH")
    payload_buf.install()
    payload_buf.push(
        {
            "filepath": [pdf_file, pdf_file],
            "answer": ['{"kasse":"AOK"}', '{"az-persnr":"12345"}'],
        }
    )
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(payload_parent)
    wpa.install()
    wpa.execute()

    data = wpa.get_buffer().data()
    assert len(data["filepath"]) == 1
    assert data["written_field_count"][0] == 2
    out_file = data["output_filepath"][0]

    reader = PdfReader(out_file)
    fields = reader.get_fields() or {}
    assert fields["kasse"]["/V"] == "AOK"
    assert fields["az-persnr"]["/V"] == "12345"


def test_merge_prefers_last_non_empty_value(tmp_path):
    pdf_file = _test_pdf_form_file()

    path_buf = ListBuffer(id="B_PDF_PATHS_MERGE_POLICY")
    path_buf.install()
    path_buf.push(pdf_file)
    path_parent = _link_buffer(path_buf)

    payload_buf = DictBuffer(id="B_PDF_FILL_MERGE_POLICY")
    payload_buf.install()
    payload_buf.push(
        {
            "filepath": [pdf_file, pdf_file, pdf_file],
            "answer": [
                '{"kasse":"AOK","az-persnr":"111"}',
                '{"kasse":"","az-persnr":""}',
                '{"kasse":"TK"}',
            ],
        }
    )
    payload_parent = _link_buffer(payload_buf)

    wpa = WritePDFFormAction(
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=_test_output_folder(),
    )
    wpa.add_parent(path_parent)
    wpa.add_parent(payload_parent)
    wpa.install()
    wpa.execute()

    out_file = wpa.get_buffer().data()["output_filepath"][0]
    reader = PdfReader(out_file)
    fields = reader.get_fields() or {}

    assert fields["kasse"]["/V"] == "TK"
    assert fields["az-persnr"]["/V"] == "111"


def test_roundtrip_read_then_write_preserves_field_values(tmp_path):
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lfa)

    wpa = WritePDFFormAction(
        require_two_parents=False,
        path_input_keys=["filepath"],
        fill_input_keys=["fields"],
        output_folder=_test_output_folder(),
        output_suffix="_roundtrip",
    )
    wpa.add_parent(rpa)

    lfa.install()
    rpa.install()
    wpa.install()

    lfa.execute()
    rpa.execute()
    wpa.execute()

    data = wpa.get_buffer().data()
    assert len(data["filepath"]) == 1
    source_file = data["filepath"][0]
    output_file = data["output_filepath"][0]

    source_values = _normalized_pdf_field_values(source_file)
    output_values = _normalized_pdf_field_values(output_file)
    assert source_values == output_values
