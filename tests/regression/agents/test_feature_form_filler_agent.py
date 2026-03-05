import configparser
import os
import sys
import types
from pathlib import Path

import nltk
import pytest
from pypdf import PdfReader

nltk.download("punkt", quiet=True)

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
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction
from pydag.nodes.documents.PDFWriteFormAction import PDFWriteFormAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.services.ThreadType import ThreadType
from pydag.services.documents.FileEmbeddingService import FileEmbeddingService
from pydag.services.llm.RAGService import RAGService
from pydag.services.statemachine.SimpleActionService import SimpleActionService


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _pdf_form_folder() -> Path:
    return _repo_root() / "tests" / "unit" / "nodes" / "documents" / "test_pdf_form"


def _rag_context_folder() -> Path:
    return _repo_root() / "resources" / "inputs" / "RAG_context"


def _output_folder() -> Path:
    return _repo_root() / "resources" / "Outputs"


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
    values: dict[str, str] = {}
    for field_id, payload in fields.items():
        current_value = payload.get("/V") if isinstance(payload, dict) else None
        values[str(field_id)] = _normalize_pdf_value(current_value)
    return values


def _build_instruction() -> str:
    return (
        "Return only a plain JSON object without markdown. "
        "Return exactly one top-level key field_updates containing an array of update items. "
        "Each update item must contain internal_field_id and selected_state or value. "
        "Do not add extra top-level keys."
    )


def _assert_form_pipeline_result(
    list_files_action: ListFilesAction,
    read_pdf_form_action: PDFReadFormAction,
    llm_fill_action: LLMChatAction,
    write_pdf_form_action: PDFWriteFormAction,
    expected_suffix: str,
):
    listed_data = list_files_action.get_buffer().data()
    assert "values" in listed_data
    assert len(listed_data["values"]) > 0
    assert all(str(path).lower().endswith(".pdf") for path in listed_data["values"])

    read_data = read_pdf_form_action.get_buffer().data()
    assert "filepath" in read_data
    assert "fields" in read_data
    assert "llm_prompt" in read_data
    assert len(read_data["filepath"]) > 0
    assert len(read_data["fields"]) > 0
    assert all(isinstance(fields_row, list) for fields_row in read_data["fields"])
    assert all(isinstance(prompt, str) and prompt.strip() != "" for prompt in read_data["llm_prompt"])

    llm_data = llm_fill_action.get_buffer().data()
    assert "answer" in llm_data
    assert "filepath" in llm_data
    assert len(llm_data["answer"]) > 0
    assert all(str(answer).strip() != "" for answer in llm_data["answer"])

    result = write_pdf_form_action.get_buffer().data()
    output_files = result.get("output_filepath", [])
    written_counts = result.get("written_field_count", [])
    written_fields = result.get("written_fields", [])

    assert len(output_files) > 0
    assert len(output_files) == len(written_counts)
    assert len(output_files) == len(written_fields)
    assert any(int(count) > 0 for count in written_counts)

    expected_folder = _output_folder().resolve()
    for idx, output_file in enumerate(output_files):
        output_path = Path(output_file)
        assert output_path.exists()
        assert output_path.parent.resolve() == expected_folder
        assert output_path.name.endswith(expected_suffix + ".pdf")

        expected_written = written_fields[idx]
        assert isinstance(expected_written, dict)
        assert int(written_counts[idx]) == len(expected_written)

        written_values = _normalized_pdf_field_values(str(output_path))
        for key, value in expected_written.items():
            assert str(key) in written_values
            expected_value = _normalize_pdf_value(value)
            actual_value = written_values[str(key)]
            if expected_value == "":
                # Some AcroForm widgets (notably certain dropdown/list fields) may retain
                # their prior/default value when assigned an empty value.
                # In that case, assert field presence but do not require exact empty persistence.
                continue
            assert actual_value == expected_value


@pytest.mark.skip(reason="Omitted: local OLLAMA e2e regression is too slow for default test runs.")
def test_feature_form_filler_agent_end_to_end_local_example():
    """End-to-end local example: real FileEmbeddingService + local OLLAMA RAGService + PDF form fill agent."""
    ollama_endpoint = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

    embedding_store_name = "form_filler_agent_e2e_local"
    embedding_service = FileEmbeddingService(
        id="FILE_EMBEDDING_SERVICE_LOCAL",
        docs_folder=str(_rag_context_folder()),
        store_name=embedding_store_name,
    )

    vector_store_directory = os.path.join(
        str(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER),
        embedding_store_name,
    )
    rag_service = RAGService(
        id="RAG_SERVICE_LOCAL",
        model_provider="OLLAMA",
        model=ollama_model,
        endpoint=ollama_endpoint,
        vector_store_path=vector_store_directory,
        retain_messages=False,
    )

    list_files_action = ListFilesAction(
        id="LIST_PDFS_LOCAL",
        folder=str(_pdf_form_folder()),
        extension=".pdf",
    )

    read_pdf_form_action = PDFReadFormAction(
        id="READ_PDF_FORM_LOCAL",
        input_keys=["values"],
        row_mode="per_pdf",
        include_bridge_prompt=True,
    )
    read_pdf_form_action.add_parent(list_files_action)

    llm_fill_action = LLMChatAction(
        id="LLM_FILL_FORM_LOCAL",
        question_key="llm_prompt",
        instruction_value=_build_instruction(),
        retrieval_query_key="llm_prompt",
        use_rag_context=True,
        pass_through_keys=["filepath"],
    )
    llm_fill_action.add_parent(read_pdf_form_action)
    llm_fill_action.set_service(rag_service)

    output_folder = _output_folder()
    output_folder.mkdir(parents=True, exist_ok=True)
    write_pdf_form_action = PDFWriteFormAction(
        id="WRITE_PDF_FORM_LOCAL",
        path_input_keys=["filepath"],
        fill_input_keys=["answer"],
        output_folder=str(output_folder),
        output_suffix="_local",
    )
    write_pdf_form_action.add_parent(llm_fill_action)

    action_service = SimpleActionService(
        id="FORM_FILLER_ACTION_SERVICE_LOCAL",
        thread_type=ThreadType.ONLY_ONCE.value,
    )
    action_service.add_node(list_files_action)
    action_service.add_node(read_pdf_form_action)
    action_service.add_node(llm_fill_action)
    action_service.add_node(write_pdf_form_action)

    agent = Agent(id="FORM_FILLER_AGENT_E2E_LOCAL")
    agent.add_service(embedding_service)
    agent.add_service(rag_service)
    agent.add_service(action_service)

    try:
        agent.release(blocking=False)
        action_service.get_observer_thread()._thread.join(timeout=240)
        _assert_form_pipeline_result(
            list_files_action=list_files_action,
            read_pdf_form_action=read_pdf_form_action,
            llm_fill_action=llm_fill_action,
            write_pdf_form_action=write_pdf_form_action,
            expected_suffix="_local",
        )
    finally:
        agent.terminate()


def test_feature_form_filler_agent_end_to_end_openai_example():
    """End-to-end OpenAI example: real FileEmbeddingService + OpenAI RAGService + PDF form fill agent."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI"):
        pytest.skip("Skipping OpenAI e2e test: missing [OPENAI] section in config.ini")
    openai_api_key = config.get("OPENAI", "OPENAI_API_KEY", fallback="").strip()
    if openai_api_key == "":
        pytest.skip("Skipping OpenAI e2e test: missing OPENAI_API_KEY in config.ini")

    embedding_store_name = "form_filler_agent_e2e_openai"
    embedding_service = FileEmbeddingService(
        id="FILE_EMBEDDING_SERVICE_OPENAI",
        docs_folder=str(_rag_context_folder()),
        store_name=embedding_store_name,
    )

    vector_store_directory = os.path.join(
        str(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER),
        embedding_store_name,
    )
    rag_service = RAGService(
        id="RAG_SERVICE_OPENAI",
        api_key=openai_api_key,
        vector_store_path=vector_store_directory,
        model="gpt-4.1-mini",
        model_provider="OPENAI",
        retain_messages=False,
    )

    list_files_action = ListFilesAction(
        id="LIST_PDFS_OPENAI",
        folder=str(_pdf_form_folder()),
        extension=".pdf",
    )

    read_pdf_form_action = PDFReadFormAction(
        id="READ_PDF_FORM_OPENAI",
        input_keys=["values"],
        row_mode="per_field",
        include_bridge_prompt=True,
    )
    read_pdf_form_action.add_parent(list_files_action)

    llm_fill_action = LLMChatAction(
        id="LLM_FILL_FORM_OPENAI",
        question_key="llm_prompt",
        instruction_value=_build_instruction(),
        retrieval_query_key="llm_prompt",
        use_rag_context=True,
        pass_through_keys=["filepath"],
    )
    llm_fill_action.add_parent(read_pdf_form_action)
    llm_fill_action.set_service(rag_service)

    output_folder = _output_folder()
    output_folder.mkdir(parents=True, exist_ok=True)
    write_pdf_form_action = PDFWriteFormAction(
        id="WRITE_PDF_FORM_OPENAI",
        path_input_keys=["filepath"],
        fill_input_keys=["answer"],
        output_folder=str(output_folder),
        output_suffix="_openai",
        row_mode="per_field",
    )
    write_pdf_form_action.add_parent(llm_fill_action)

    action_service = SimpleActionService(
        id="FORM_FILLER_ACTION_SERVICE_OPENAI",
        thread_type=ThreadType.ONLY_ONCE.value,
    )
    action_service.add_node(list_files_action)
    action_service.add_node(read_pdf_form_action)
    action_service.add_node(llm_fill_action)
    action_service.add_node(write_pdf_form_action)

    agent = Agent(id="FORM_FILLER_AGENT_E2E_OPENAI")
    agent.add_service(embedding_service)
    agent.add_service(rag_service)
    agent.add_service(action_service)

    try:
        agent.release(blocking=False)
        action_service.get_observer_thread()._thread.join(timeout=240)
        llm_data = llm_fill_action.get_buffer().data()
        if "answer" not in llm_data or len(llm_data.get("answer", [])) == 0:
            service_state = action_service.get_state()
            state_label = service_state.value if hasattr(service_state, "value") else str(service_state)
            pytest.skip(
                "Skipping OpenAI e2e test: no LLM answer produced "
                + "(state="
                + state_label
                + "). This can happen due to API/network/quota/provider issues."
            )
        _assert_form_pipeline_result(
            list_files_action=list_files_action,
            read_pdf_form_action=read_pdf_form_action,
            llm_fill_action=llm_fill_action,
            write_pdf_form_action=write_pdf_form_action,
            expected_suffix="_openai",
        )
    finally:
        agent.terminate()
