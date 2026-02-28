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


def _fixture_extracted_field_count() -> int:
    rpa = ReadPDFFormAction()
    return len(rpa._read_pdf(_test_pdf_form_file())["fields"])


def _expected_rows_for_pdf_count(
    fixture_field_count: int, pdf_count: int, fields_output_mode: str
) -> int:
    if fields_output_mode == "per_pdf":
        return pdf_count
    return (pdf_count * fixture_field_count) if fixture_field_count > 0 else pdf_count


def _assert_fields_layout(field_rows: list[list[dict]], fixture_field_count: int, fields_output_mode: str):
    assert all(isinstance(row_fields, list) for row_fields in field_rows)
    if fields_output_mode == "per_pdf":
        expected_len = fixture_field_count if fixture_field_count > 0 else 0
        assert all(len(row_fields) == expected_len for row_fields in field_rows)
    elif fixture_field_count > 0:
        assert all(len(row_fields) == 1 for row_fields in field_rows)
    else:
        assert all(len(row_fields) == 0 for row_fields in field_rows)


def _contains_field_id(field_rows: list[list[dict]], field_id: str) -> bool:
    return any(field.get("field_id") == field_id for row_fields in field_rows for field in row_fields)


def _count_field_id(field_rows: list[list[dict]], field_id: str) -> int:
    return sum(1 for row_fields in field_rows for field in row_fields if field.get("field_id") == field_id)


def _iter_fields(field_rows: list[list[dict]]):
    for row_fields in field_rows:
        for field in row_fields:
            yield field


def _assert_enriched_field_payload(field_rows: list[list[dict]]):
    all_fields = list(_iter_fields(field_rows))
    if len(all_fields) == 0:
        return
    required_keys = {
        "field_id",
        "write_target_field_id",
        "field_type",
        "label_context",
        "current_value",
        "proposed_value",
        "rect",
        "is_fillable",
        "context_bundle",
        "value_profile",
        "retrieval_query",
        "context_confidence",
        "needs_review",
    }
    for field in all_fields:
        assert required_keys.issubset(set(field.keys()))
        assert field["is_fillable"] is True
        assert isinstance(field["write_target_field_id"], str)
        assert field["write_target_field_id"] != ""
        assert field["proposed_value"] == ""
        assert isinstance(field["context_bundle"], dict)
        assert isinstance(field["value_profile"], dict)
        assert isinstance(field["retrieval_query"], str)
        assert isinstance(field["context_confidence"], float)
        assert isinstance(field["needs_review"], bool)


@pytest.mark.parametrize("fields_output_mode", ["per_field", "per_pdf"])
def test_reads_pdf_from_list_files_parent_and_writes_structured_output(fields_output_mode: str):
    """Integration: read PDF via ListFilesAction and assert structured output with non-empty text/fields."""
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(input_keys=["values"], fields_output_mode=fields_output_mode)
    rpa.add_parent(lfa)

    lfa.install()
    rpa.install()

    lfa.execute()
    rpa.execute()

    data = rpa.get_buffer().data()

    expected_file = os.path.basename(_test_pdf_form_file())
    fixture_field_count = _fixture_extracted_field_count()
    expected_rows = _expected_rows_for_pdf_count(
        fixture_field_count=fixture_field_count,
        pdf_count=1,
        fields_output_mode=fields_output_mode,
    )
    assert "filepath" in data
    assert len(data["filepath"]) == expected_rows
    assert all(path.endswith(expected_file) for path in data["filepath"])
    assert "metadata" in data
    assert len(data["metadata"]) == expected_rows
    assert all(meta["pages"] >= 1 for meta in data["metadata"])
    assert "fields" in data
    assert len(data["fields"]) == expected_rows
    _assert_fields_layout(data["fields"], fixture_field_count, fields_output_mode)
    _assert_enriched_field_payload(data["fields"])
    assert _contains_field_id(data["fields"], "kasse")
    assert "full_text_content" in data
    assert len(data["full_text_content"]) == expected_rows
    assert all(len(text) > 0 for text in data["full_text_content"])
    assert all("Besoldung" in text for text in data["full_text_content"])


@pytest.mark.parametrize("fields_output_mode", ["per_field", "per_pdf"])
def test_reads_same_pdf_twice_and_writes_expected_rows_for_each_pdf(fields_output_mode: str):
    """Verify row count scales with field count and selected output mode when reading the same PDF twice."""
    pdf_file = _test_pdf_form_file()

    buf = ListBuffer(id="B_MULTI_PDF")
    buf.install()
    buf.push(pdf_file)
    buf.push(pdf_file)

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"], fields_output_mode=fields_output_mode)
    rpa.add_parent(lba)
    rpa.install()
    rpa.execute()

    data = rpa.get_buffer().data()

    expected_file = os.path.basename(_test_pdf_form_file())
    fixture_field_count = _fixture_extracted_field_count()
    expected_rows = _expected_rows_for_pdf_count(
        fixture_field_count=fixture_field_count,
        pdf_count=2,
        fields_output_mode=fields_output_mode,
    )
    assert "filepath" in data
    assert len(data["filepath"]) == expected_rows
    assert all(path.endswith(expected_file) for path in data["filepath"])
    assert len(data["metadata"]) == expected_rows
    assert all(meta["pages"] >= 1 for meta in data["metadata"])
    assert len(data["fields"]) == expected_rows
    _assert_fields_layout(data["fields"], fixture_field_count, fields_output_mode)
    _assert_enriched_field_payload(data["fields"])
    assert _count_field_id(data["fields"], "kasse") >= 2
    assert len(data["full_text_content"]) == expected_rows
    assert all("Besoldung" in text for text in data["full_text_content"])


@pytest.mark.parametrize("fields_output_mode", ["per_field", "per_pdf"])
def test_reads_pdf_from_dictbuffer_parent_link(fields_output_mode: str):
    """Verify parent-link extraction when the parent buffer is a DictBuffer with a valid path key."""
    pdf_file = _test_pdf_form_file()

    parent_buf = DictBuffer(id="B_DICT_PARENT")
    parent_buf.install()
    parent_buf.push({"values": pdf_file})

    lba = LinkBufferAction()
    lba.set_buffer(parent_buf)
    lba.install()

    rpa = ReadPDFFormAction(input_keys=["values"], fields_output_mode=fields_output_mode)
    rpa.add_parent(lba)
    rpa.install()
    rpa.execute()

    data = rpa.get_buffer().data()
    expected_file = os.path.basename(pdf_file)
    fixture_field_count = _fixture_extracted_field_count()
    expected_rows = _expected_rows_for_pdf_count(
        fixture_field_count=fixture_field_count,
        pdf_count=1,
        fields_output_mode=fields_output_mode,
    )

    assert "filepath" in data
    assert len(data["filepath"]) == expected_rows
    assert all(path.endswith(expected_file) for path in data["filepath"])
    assert "fields" in data
    assert len(data["fields"]) == expected_rows
    _assert_fields_layout(data["fields"], fixture_field_count, fields_output_mode)
    _assert_enriched_field_payload(data["fields"])
    assert _contains_field_id(data["fields"], "kasse")
    assert "full_text_content" in data
    assert len(data["full_text_content"]) == expected_rows
    assert all("Besoldung" in text for text in data["full_text_content"])


@pytest.mark.parametrize("fields_output_mode", ["per_field", "per_pdf"])
def test_agent_pipeline_executes_list_and_read_actions_only_once(fields_output_mode: str):
    """Agent-level pipeline test: ONLY_ONCE service should produce parsed rows for both output modes."""
    agent = Agent(id="PDF_AGENT")

    service = SimpleActionService(id="PDF_SVC", thread_type=ThreadType.ONLY_ONCE.value)
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(input_keys=["values"], fields_output_mode=fields_output_mode)
    rpa.add_parent(lfa)

    service.add_node(lfa)
    service.add_node(rpa)
    agent.add_service(service)

    try:
        agent.release(blocking=False)
        service.get_observer_thread()._thread.join(timeout=3)

        data = rpa.get_buffer().data()
        expected_file = os.path.basename(_test_pdf_form_file())
        fixture_field_count = _fixture_extracted_field_count()
        expected_rows = _expected_rows_for_pdf_count(
            fixture_field_count=fixture_field_count,
            pdf_count=1,
            fields_output_mode=fields_output_mode,
        )
        assert "filepath" in data
        assert len(data["filepath"]) == expected_rows
        assert all(path.endswith(expected_file) for path in data["filepath"])
        assert all(meta["pages"] >= 1 for meta in data["metadata"])
        _assert_fields_layout(data["fields"], fixture_field_count, fields_output_mode)
        _assert_enriched_field_payload(data["fields"])
        assert _contains_field_id(data["fields"], "kasse")
        assert all("Besoldung" in text for text in data["full_text_content"])
    finally:
        agent.terminate()



def test_install_creates_default_dict_buffer():
    """Ensure install creates/links a DictBuffer by default."""
    rpa = ReadPDFFormAction()
    rpa.install()

    assert isinstance(rpa.get_buffer(), DictBuffer)
    assert rpa.buffer_id is not None


def test_install_raises_for_invalid_fields_output_mode():
    rpa = ReadPDFFormAction(fields_output_mode="invalid")
    with pytest.raises(NodeException):
        rpa.install()


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


@pytest.mark.parametrize("fields_output_mode", ["per_field", "per_pdf"])
def test_custom_output_keys_are_used(fields_output_mode: str):
    """Custom output_keys should rename output columns while preserving values."""
    lfa = ListFilesAction(folder=_test_pdf_form_folder(), extension=".pdf")
    rpa = ReadPDFFormAction(
        input_keys=["values"],
        output_keys=["pdf", "meta", "form_fields", "text"],
        fields_output_mode=fields_output_mode,
    )
    rpa.add_parent(lfa)

    lfa.install()
    rpa.install()

    lfa.execute()
    rpa.execute()

    data = rpa.get_buffer().data()
    expected_file = os.path.basename(_test_pdf_form_file())
    fixture_field_count = _fixture_extracted_field_count()
    expected_rows = _expected_rows_for_pdf_count(
        fixture_field_count=fixture_field_count,
        pdf_count=1,
        fields_output_mode=fields_output_mode,
    )

    assert "pdf" in data
    assert "meta" in data
    assert "form_fields" in data
    assert "text" in data
    assert "filepath" not in data
    assert "metadata" not in data
    assert "fields" not in data
    assert "full_text_content" not in data
    assert len(data["pdf"]) == expected_rows
    assert all(path.endswith(expected_file) for path in data["pdf"])
    assert len(data["form_fields"]) == expected_rows
    _assert_fields_layout(data["form_fields"], fixture_field_count, fields_output_mode)


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
    assert first_field["write_target_field_id"] == "Date_01"
    assert first_field["field_type"] == "/Text"
    assert first_field["current_value"] == "2024-01-01"
    assert first_field["proposed_value"] == ""
    assert first_field["is_fillable"] is True
    assert first_field["rect"] == [80.0, 90.0, 180.0, 110.0]
    assert "Geburtsdatum" in first_field["label_context"]
    assert isinstance(first_field["context_bundle"], dict)
    assert isinstance(first_field["value_profile"], dict)
    assert isinstance(first_field["retrieval_query"], str)
    assert isinstance(first_field["context_confidence"], float)
    assert isinstance(first_field["needs_review"], bool)

def test_fixture_pdf_has_acroform_fields():
    """Sanity check: fixture PDF must expose real AcroForm fields (guard against bad test assets)."""
    reader = PdfReader(_test_pdf_form_file())
    fields = reader.get_fields()

    assert fields is not None
    assert len(fields) > 0
    assert "kasse" in fields
