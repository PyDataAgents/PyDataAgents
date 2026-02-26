import configparser
import os
import sys
import types
import uuid
from pathlib import Path

import numpy as np
import numpy  # Explicitly ensure numpy is available for embedding service
import nltk
nltk.download('punkt', quiet=True)

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
from pydag.nodes.documents.ReadPDFFormAction import ReadPDFFormAction
from pydag.nodes.documents.WritePDFFormAction import WritePDFFormAction
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
    return _repo_root() / "resources" / "outputs"


def _build_instruction() -> str:
    return (
        "Return only a plain JSON object without markdown.\n"
        "You must return exactly the same json keys as in the input context. Do NOT add any keys. Fill the field 'current_value' with your answer but with values filled in based on the retrieved RAG context.\n"
        "Where <field_id> is the key from the input context and <current_value> is the inferred value.\n"
    )


def test_feature_form_filler_agent_end_to_end_local_example():
    """End-to-end local example: real FileEmbeddingService + local OLLAMA RAGService + PDF form fill Agent."""
    ollama_endpoint = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "deepseek-r1")

    embedding_store_name = "form_filler_agent_e2e_local_" + uuid.uuid4().hex[0:8]
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

    read_pdf_form_action = ReadPDFFormAction(
        id="READ_PDF_FORM_LOCAL",
        input_keys=["values"],
    )
    read_pdf_form_action.add_parent(list_files_action)

    llm_fill_action = LLMChatAction(
        id="LLM_FILL_FORM_LOCAL",
        question_value="Fill the PDF form fields in the input context with values from the retrieved context. ",
        instruction_value=_build_instruction(),
        retrieval_query_key="fields",
        input_context_keys=["fields"],
        pass_through_keys=["filepath"],
        use_rag_context=True,
    )
    llm_fill_action.add_parent(read_pdf_form_action)
    llm_fill_action.set_service(rag_service)

    output_folder = _output_folder()
    output_folder.mkdir(parents=True, exist_ok=True)
    write_pdf_form_action = WritePDFFormAction(
        id="WRITE_PDF_FORM_LOCAL",
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=str(output_folder),
        output_suffix="_local",
    )
    write_pdf_form_action.add_parent(list_files_action)
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
    # Start order matters: embeddings first, then RAG, then action pipeline.
    agent.add_service(embedding_service)
    agent.add_service(rag_service)
    agent.add_service(action_service)

    try:
        agent.release(blocking=False)
        action_service.get_observer_thread()._thread.join()

        result = write_pdf_form_action.get_buffer().data()
        output_files = result.get("output_filepath", [])
        written_counts = result.get("written_field_count", [])
        written_fields = result.get("written_fields", [])

        print("Local form filler agent finished.")
        print("OLLAMA endpoint:", ollama_endpoint)
        print("OLLAMA model:", ollama_model)
        print("Output files:", output_files)
        print("Written field counts:", written_counts)
        if len(written_fields) > 0:
            print("Written field keys:", list(written_fields[0].keys()))
    finally:
        agent.terminate()


def test_feature_form_filler_agent_end_to_end_openai_example():
    """End-to-end OpenAI example: real FileEmbeddingService + default OpenAI RAGService + PDF form fill Agent."""
    config = configparser.ConfigParser()
    config.read("config.ini")

    embedding_store_name = "form_filler_agent_e2e_openai_" + uuid.uuid4().hex[0:8]
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
        api_key=config["OPENAI"]["OPENAI_API_KEY"],
        vector_store_path=vector_store_directory,
        retain_messages=False,
    )

    list_files_action = ListFilesAction(
        id="LIST_PDFS_OPENAI",
        folder=str(_pdf_form_folder()),
        extension=".pdf",
    )

    read_pdf_form_action = ReadPDFFormAction(
        id="READ_PDF_FORM_OPENAI",
        input_keys=["values"],
    )
    read_pdf_form_action.add_parent(list_files_action)

    llm_fill_action = LLMChatAction(
        id="LLM_FILL_FORM_OPENAI",
        question_value="Fill the PDF form fields in the input context with values from the retrieved context. ",
        instruction_value=_build_instruction(),
        retrieval_query_key="fields",
        input_context_keys=["fields"],
        pass_through_keys=["filepath"],
        use_rag_context=True,
    )
    llm_fill_action.add_parent(read_pdf_form_action)
    llm_fill_action.set_service(rag_service)

    output_folder = _output_folder()
    output_folder.mkdir(parents=True, exist_ok=True)
    write_pdf_form_action = WritePDFFormAction(
        id="WRITE_PDF_FORM_OPENAI",
        path_input_keys=["values"],
        fill_input_keys=["answer"],
        output_folder=str(output_folder),
        output_suffix="_openai",
    )
    write_pdf_form_action.add_parent(list_files_action)
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
    # Start order matters: embeddings first, then RAG, then action pipeline.
    agent.add_service(embedding_service)
    agent.add_service(rag_service)
    agent.add_service(action_service)

    try:
        agent.release(blocking=False)
        action_service.get_observer_thread()._thread.join()

        result = write_pdf_form_action.get_buffer().data()
        output_files = result.get("output_filepath", [])
        written_counts = result.get("written_field_count", [])
        written_fields = result.get("written_fields", [])

        print("OpenAI form filler agent finished.")
        print("OPENAI model provider:", rag_service.model_provider)
        print("OPENAI model:", rag_service.model)
        print("Output files:", output_files)
        print("Written field counts:", written_counts)
        if len(written_fields) > 0:
            print("Written field keys:", list(written_fields[0].keys()))
    finally:
        agent.terminate()
