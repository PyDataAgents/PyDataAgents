import os
import sys
import types

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

from pydag.agents.Agent import Agent
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.documents.ReadPDFFormAction import ReadPDFFormAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleActionService import SimpleActionService


def _test_pdf_form_folder() -> str:
    return os.path.join(os.path.dirname(__file__), "test_pdf_form")


def _test_pdf_form_file() -> str:
    """Return the first PDF fixture in test_pdf_form (expected: AcroForm-enabled PDF)."""
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

def test_reads_pdf_from_list_files_parent_and_writes_structured_output():
    """Integration: read PDF via ListFilesAction and assert structured output with non-empty text/fields."""
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lfa)

    lfa.install()
    rpa.install()

    lfa.execute()
    rpa.execute()

    data = rpa.get_buffer().data()

    expected_file = os.path.basename(_test_pdf_form_file())
    assert "filepath" in data
    assert data["filepath"][0].endswith(expected_file)
    assert "metadata" in data
    assert data["metadata"][0]["pages"] >= 1
    assert "fields" in data
    assert isinstance(data["fields"][0], list)
    assert len(data["fields"][0]) > 0
    assert any(f.get("field_id") == "kasse" for f in data["fields"][0])
    assert "full_text_content" in data
    assert len(data["full_text_content"][0]) > 0
    assert "Besoldung" in data["full_text_content"][0]


def test_reads_same_pdf_twice_and_writes_two_rows():
    """Verify multi-PDF behavior by pushing the same fixture twice and expecting two output rows."""
    pdf_file = _test_pdf_form_file()

    buf = ListBuffer(id="B_MULTI_PDF")
    buf.install()
    buf.push(pdf_file)
    buf.push(pdf_file)

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lba)
    rpa.install()
    rpa.execute()

    data = rpa.get_buffer().data()

    expected_file = os.path.basename(_test_pdf_form_file())
    assert "filepath" in data
    assert len(data["filepath"]) == 2
    assert data["filepath"][0].endswith(expected_file)
    assert data["filepath"][1].endswith(expected_file)
    assert len(data["metadata"]) == 2
    assert data["metadata"][0]["pages"] >= 1
    assert data["metadata"][1]["pages"] >= 1
    assert len(data["fields"]) == 2
    assert isinstance(data["fields"][0], list)
    assert isinstance(data["fields"][1], list)
    assert len(data["fields"][0]) > 0
    assert len(data["fields"][1]) > 0
    assert any(f.get("field_id") == "kasse" for f in data["fields"][0])
    assert any(f.get("field_id") == "kasse" for f in data["fields"][1])
    assert len(data["full_text_content"]) == 2
    assert "Besoldung" in data["full_text_content"][0]
    assert "Besoldung" in data["full_text_content"][1]


def test_reads_pdf_from_dictbuffer_parent_link():
    """Verify parent-link extraction when the parent buffer is a DictBuffer with a valid path key."""
    pdf_file = _test_pdf_form_file()

    parent_buf = DictBuffer(id="B_DICT_PARENT")
    parent_buf.install()
    parent_buf.push({"values": pdf_file})

    lba = LinkBufferAction()
    lba.set_buffer(parent_buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lba)
    rpa.install()
    rpa.execute()

    data = rpa.get_buffer().data()
    expected_file = os.path.basename(pdf_file)

    assert "filepath" in data
    assert len(data["filepath"]) == 1
    assert data["filepath"][0].endswith(expected_file)
    assert "fields" in data
    assert len(data["fields"][0]) > 0
    assert any(f.get("field_id") == "kasse" for f in data["fields"][0])
    assert "full_text_content" in data
    assert "Besoldung" in data["full_text_content"][0]


def test_agent_pipeline_executes_list_and_read_actions_only_once():
    """Agent-level pipeline test: ONLY_ONCE service should produce one parsed result row."""
    agent = Agent(id="PDF_AGENT")

    service = SimpleActionService(id="PDF_SVC", thread_type=ThreadType.ONLY_ONCE.value)
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lfa)

    service.add_node(lfa)
    service.add_node(rpa)
    agent.add_service(service)

    try:
        agent.release(blocking=False)
        service.get_observer_thread()._thread.join(timeout=3)

        data = rpa.get_buffer().data()
        expected_file = os.path.basename(_test_pdf_form_file())
        assert "filepath" in data
        assert data["filepath"][0].endswith(expected_file)
        assert data["metadata"][0]["pages"] >= 1
        assert isinstance(data["fields"][0], list)
        assert len(data["fields"][0]) > 0
        assert any(f.get("field_id") == "kasse" for f in data["fields"][0])
        assert "Besoldung" in data["full_text_content"][0]
    finally:
        agent.terminate()



def test_install_creates_default_dict_buffer():
    """Ensure install creates/links a DictBuffer by default."""
    rpa = ReadPDFFormAction()
    rpa.install()

    assert isinstance(rpa.get_buffer(), DictBuffer)
    assert rpa.buffer_id is not None


def test_execute_raises_without_parent_data():
    """Execution without parent buffer data should fail fast."""
    rpa = ReadPDFFormAction()
    rpa.install()

    with pytest.raises(NodeException):
        rpa.execute()


def test_execute_raises_for_non_pdf_path_from_parent():
    """Non-PDF parent input should be rejected when require_pdf_extension is enabled."""
    buf = ListBuffer(id="B_NONPDF")
    buf.install()
    buf.push(os.path.join(os.path.dirname(__file__), "test.csv"))

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lba)
    rpa.install()

    with pytest.raises(NodeException):
        rpa.execute()


def test_execute_raises_for_missing_pdf_file(tmp_path):
    """Missing PDF paths should raise NodeException."""
    missing_pdf = str(tmp_path / "missing.pdf")

    buf = ListBuffer(id="B_MISSING")
    buf.install()
    buf.push(missing_pdf)

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lba)
    rpa.install()

    with pytest.raises(NodeException):
        rpa.execute()


def test_custom_output_keys_are_used():
    """Custom output_keys should rename output columns while preserving values."""
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(
        input_keys=["values"],
        output_keys=["pdf", "meta", "form_fields", "text"],
    )
    rpa.add_parent(lfa)

    lfa.install()
    rpa.install()

    lfa.execute()
    rpa.execute()

    data = rpa.get_buffer().data()
    expected_file = os.path.basename(_test_pdf_form_file())

    assert "pdf" in data
    assert "meta" in data
    assert "form_fields" in data
    assert "text" in data
    assert "filepath" not in data
    assert "metadata" not in data
    assert "fields" not in data
    assert "full_text_content" not in data
    assert data["pdf"][0].endswith(expected_file)


def test_extracts_field_structure_and_label_context_with_mocked_pdfreader(monkeypatch, tmp_path):
    """Unit test for field normalization and label inference using a mocked PdfReader."""
    import pydag.nodes.documents.ReadPDFFormAction as read_pdf_module

    class FakeAnnotRef:
        def __init__(self, obj):
            self._obj = obj

        def get_object(self):
            return self._obj

    class FakePage:
        def __init__(self):
            self._annots = [
                FakeAnnotRef(
                    {
                        "/Subtype": "/Widget",
                        "/T": "Date_01",
                        "/FT": "/Text",
                        "/V": "2024-01-01",
                        "/Rect": [80, 90, 180, 110],
                    }
                )
            ]

        def get(self, key, default=None):
            if key == "/Annots":
                return self._annots
            return default

        def extract_text(self, visitor_text=None):
            if visitor_text is not None:
                visitor_text(
                    "Geburtsdatum",
                    [1, 0, 0, 1, 10, 100],
                    [1, 0, 0, 1, 10, 100],
                    None,
                    12,
                )
            return "Mock page text"

    class FakePdfReader:
        def __init__(self, file_path):
            self.file_path = file_path
            self.pages = [FakePage()]
            self.metadata = {"/Producer": "FakePDF"}

        def get_fields(self):
            return {
                "Date_01": {
                    "/T": "Date_01",
                    "/FT": "/Text",
                    "/V": "2024-01-01",
                    "/Rect": [80, 90, 180, 110],
                }
            }

    monkeypatch.setattr(read_pdf_module, "PdfReader", FakePdfReader)

    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%fake\n")

    buf = ListBuffer(id="B_FAKE")
    buf.install()
    buf.push(str(fake_pdf))

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"])
    rpa.add_parent(lba)
    rpa.install()
    rpa.execute()

    data = rpa.get_buffer().data()

    assert data["metadata"][0]["pages"] == 1
    assert data["metadata"][0]["Producer"] == "FakePDF"
    assert data["full_text_content"][0] == "Mock page text"

    fields = data["fields"][0]
    assert len(fields) == 1
    first_field = fields[0]
    assert first_field["field_id"] == "Date_01"
    assert first_field["field_type"] == "/Text"
    assert first_field["current_value"] == "2024-01-01"
    assert first_field["rect"] == [80.0, 90.0, 180.0, 110.0]
    assert "Geburtsdatum" in first_field["label_context"]

def test_fixture_pdf_has_acroform_fields():
    """Sanity check: fixture PDF must expose real AcroForm fields (guard against bad test assets)."""
    reader = PdfReader(_test_pdf_form_file())
    fields = reader.get_fields()

    assert fields is not None
    assert len(fields) > 0
    assert "kasse" in fields
