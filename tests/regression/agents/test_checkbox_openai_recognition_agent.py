import configparser
import json
import os
import sys
import types
from pathlib import Path

from langchain_openai import ChatOpenAI
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
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction
from pydag.nodes.documents.PDFWriteFormAction import PDFWriteFormAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.services.llm.RAGService import RAGService


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _test_pdf_file() -> str:
    return str(_repo_root() / "tests" / "unit" / "nodes" / "documents" / "test_pdf_form" / "test_5031.pdf")


def _output_folder() -> Path:
    return _repo_root() / "resources" / "Outputs"


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


def _link_buffer(buffer):
    lba = LinkBufferAction()
    lba.set_buffer(buffer)
    lba.install()
    return lba


def _require_fitz_for_pdf_form_tests():
    try:
        import fitz  # type: ignore  # noqa: F401
    except Exception as exc:
        raise AssertionError("PyMuPDF (fitz) is required for live checkbox recognition regression tests") from exc


class _OpenAIChatOnlyRAGService(RAGService):
    """OpenAI-backed RAGService variant without embedding/retriever startup."""

    def _on_start(self):
        self._retriever = None
        self._embedding_store = None
        self._embedding_model = None
        self._create_llm_and_chain()

    def _create_llm(self):
        self._llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key, temperature=0)


def _is_kindergeld_section(field: dict) -> bool:
    section_hint = " ".join(
        [
            str(field.get("generated_question", "")),
            str(field.get("question_context", "")),
            str(field.get("option_text", "")),
            str(field.get("question_text", "")),
            str(field.get("section_header", "")),
            str(field.get("page_context", "")),
        ]
    ).lower()
    return any(
        marker in section_hint
        for marker in ["538b2", "familienzuschlag", "angaben zu kindern", "bundeskindergeldgesetz"]
    )


def test_openai_recognizes_checkbox_value_and_writer_checks_kindergeld_yes_option():
    _require_fitz_for_pdf_form_tests()

    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI"):
        pytest.skip("Skipping live checkbox recognition test: missing [OPENAI] in config.ini")
    if not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping live checkbox recognition test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    api_key = config.get("OPENAI", "OPENAI_API_KEY")

    path_buf = ListBuffer(id="B_CHECKBOX_OPENAI_PATH")
    path_buf.install()
    path_buf.push(_test_pdf_file())
    path_parent = _link_buffer(path_buf)

    reader_action = PDFReadFormAction(
        id="READ_KINDERGELD_FIELD",
        input_keys=["values"],
        row_mode="per_field",
        include_bridge_prompt=True,
    )
    reader_action.add_parent(path_parent)
    reader_action.install()
    reader_action.execute()

    read_data = reader_action.get_buffer().data()
    rows = list(zip(read_data.get("filepath", []), read_data.get("fields", []), read_data.get("llm_prompt", [])))
    checkbox_rows = [row for row in rows if len(row[1]) == 1 and row[1][0].get("field_type") in {"checkbox", "radio"}]

    target_field = ""
    opposite_field = ""
    checkbox_filepath = ""
    checkbox_prompt = ""
    for row in checkbox_rows:
        field = row[1][0]
        if not _is_kindergeld_section(field):
            continue
        option_text = str(field.get("option_text", "")).lower()
        internal_field_id = str(field.get("internal_field_id", "")).strip()
        if (" ja" in " " + option_text or option_text.startswith("ja")) and internal_field_id != "":
            target_field = internal_field_id
            checkbox_filepath = str(row[0])
            checkbox_prompt = str(row[2])
        if (" nein" in " " + option_text or option_text.startswith("nein")) and internal_field_id != "":
            opposite_field = internal_field_id

    assert target_field != ""
    assert opposite_field != ""
    assert checkbox_filepath != ""
    assert checkbox_prompt.strip() != ""

    llm_input_buf = DictBuffer(id="B_CHECKBOX_OPENAI_LLM_INPUT")
    llm_input_buf.install()
    llm_input_buf.push({"filepath": checkbox_filepath, "llm_prompt": checkbox_prompt})
    llm_input_parent = _link_buffer(llm_input_buf)

    service = _OpenAIChatOnlyRAGService(
        id="RAG_CHECKBOX_OPENAI",
        api_key=api_key,
        model_provider="OPENAI",
        model="gpt-4.1-mini",
        retain_messages=False,
    )
    service.install()
    service.start()
    try:
        llm_action = LLMChatAction(
            id="LLM_CHECKBOX_OPENAI",
            question_key="llm_prompt",
            instruction_value=(
                "Return only JSON object without markdown. "
                "Return exactly one top-level key field_updates containing an array of update items. "
                "Each update item must contain internal_field_id and selected_state or value. "
                "For checkbox/radio use selected_state and one of the field button_states from the prompt. "
                f"Context facts are authoritative for this task: {target_field}: Ja. "
                "For this target field do not return empty and do not return Off."
            ),
            use_rag_context=False,
            pass_through_keys=["filepath"],
        )
        llm_action.add_parent(llm_input_parent)
        llm_action.set_service(service)
        llm_action.install()
        llm_action.execute()

        llm_data = llm_action.get_buffer().data()
        answers = llm_data.get("answer", [])
        assert len(answers) == 1
        raw_answer = str(answers[0])
        parsed_answer = json.loads(raw_answer)
        assert isinstance(parsed_answer, dict)
        updates = parsed_answer.get("field_updates")
        assert isinstance(updates, list)
        target_updates = [
            item
            for item in updates
            if isinstance(item, dict) and str(item.get("internal_field_id", "")).strip() == target_field
        ]
        assert len(target_updates) == 1
        target_value = _normalize_pdf_name(target_updates[0].get("selected_state"))
        assert target_value.lower() == "ja", "Model did not recognize checkbox intent. Raw answer: " + raw_answer

        output_folder = _output_folder()
        output_folder.mkdir(parents=True, exist_ok=True)
        write_action = PDFWriteFormAction(
            id="WRITE_CHECKBOX_OPENAI",
            path_input_keys=["filepath"],
            fill_input_keys=["answer"],
            output_folder=str(output_folder),
            output_suffix="_checkbox_openai_live_yes",
        )
        write_action.add_parent(llm_action)
        write_action.install()
        write_action.execute()

        out_data = write_action.get_buffer().data()
        assert len(out_data.get("output_filepath", [])) == 1
        written_fields_rows = out_data.get("written_fields", [])
        assert len(written_fields_rows) == 1
        written_fields = written_fields_rows[0]
        assert isinstance(written_fields, dict)
        assert _normalize_pdf_name(written_fields.get(target_field)).lower() == "ja"
        output_pdf_path = str(out_data["output_filepath"][0])
        assert os.path.isfile(output_pdf_path)

        output_field_state = _raw_field_value(output_pdf_path, target_field)
        output_widget_states = _widget_appearance_states(output_pdf_path, target_field)
        assert output_field_state.lower() == "ja", "Written field state is not Ja for " + target_field
        assert any(state.lower() == "ja" for state in output_widget_states), (
            "Widget appearance state is not Ja for " + target_field + ". States: " + str(output_widget_states)
        )

        opposite_output_state = _raw_field_value(output_pdf_path, opposite_field)
        assert opposite_output_state in {"", "Off"}
    finally:
        service.stop()


def test_openai_recognizes_checkbox_value_and_writer_checks_kindergeld():
    # Backward-compatible alias for older test selectors.
    test_openai_recognizes_checkbox_value_and_writer_checks_kindergeld_yes_option()
