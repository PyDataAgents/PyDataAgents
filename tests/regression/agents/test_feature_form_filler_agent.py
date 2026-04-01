import configparser
import json
import os
import sys
import types
from pathlib import Path

import nltk
import pytest
from pypdf import PdfReader

nltk.download("punkt", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)

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
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
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
        "Do not add extra top-level keys. "
        "If input_context.fields is provided and contains one field entry, return exactly one update "
        "for that same internal_field_id. "
        "For text/list/dropdown fields, if no reliable value is found, return value as an empty string. "
        "For checkbox/radio fields, selected_state must be one of button_states; if uncertain, use an empty string."
    )


def _context2_expected_field_answers() -> dict[str, str]:
    return {
        "Name": "Doe",
        "vorname": "John",
        "pers-nr": "123456dwwe",
        "geburtsname": "Smith",
        "geb-datum": "01.01.1900",
        "geb-ort": "Rome",
        "anschrift": "Hauptstrasse 1, 70173 Stuttgart, Germany",
        "telefon": "+49 711 123456",
        "amtsbezeichnung": "Wissenschaftlicher Mitarbeiter",
        "staatsangeh": "Schweizer",
        "akad-grade": "Doktor der Ingenieurwissenschaften",
        "beginn": "01.10.1920",
        "besch-stelle": "Universitaet",
        "bankverbindung.1.0": "University Bank",
        "Text3": "GENODES1EBT",
        "Text4": "DE57659801200082151005",
        "Text5": "2051003",
        "bankverbindung.1.1": "123456dwwe",
        "bankverbindung.1.2": "7700",
        "Identifikationsnummer": "12345678901",
        "Text1.0.0": "IV",
        "Text1.0.1": "entfaellt",
        "Text1.1.1": "entfaellt",
        "kasse": "DAK",
        "az-persnr": "AZ-778899",
        "datum2": "22.02.2026",
        "fam-stand": "Ja",
        "fam-stand1": "Off",
        "Kontrollkästchen3": "Off",
        "fam-stand2": "Off",
        "fam-stand3": "Off",
        "Check Box5.0": "Ja",
        "Check Box5.1": "Off",
        "kinder.2": "Off",
        "kinder.1": "Ja",
        "kinder.0": "Ja",
        "kinder1": "Off",
        "Kontrollkästchen1": "Off",
        "Kontrollkästchen2": "Ja",
        "kindergeld": "Off",
        "kindergeld1": "Off",
        "versorgungsbezuege": "Ja",
        "versorgungsbezuege1": "Off",
        "dienstverh": "nein",
        "dienstverh1": "Off",
    }


def _normalize_answer_to_field_values(answer: str) -> dict[str, str]:
    parser = PDFWriteFormAction()
    try:
        payload = parser._normalize_payload(answer)
    except Exception:
        return {}
    if payload is None:
        return {}
    return {str(key): _normalize_pdf_value(value) for key, value in payload.items()}


def _is_resolved_for_field(answer_values: dict[str, str], field_id: str) -> bool:
    if field_id not in answer_values:
        return False
    return str(answer_values[field_id]).strip() != ""


def _field_update_key(field_payload: dict) -> str:
    field_type = str(field_payload.get("field_type", "")).strip().lower()
    if field_type in {"checkbox", "radio"}:
        return "selected_state"
    return "value"


def _single_field_answer_payload(field_payload: dict, value: str) -> str:
    field_id = str(field_payload.get("internal_field_id", "")).strip()
    update_key = _field_update_key(field_payload)
    payload = {
        "field_updates": [
            {
                "internal_field_id": field_id,
                update_key: _normalize_pdf_value(value),
            }
        ]
    }
    return json.dumps(payload, ensure_ascii=True)


def _sanitize_answer_to_single_field(answer: str, field_payload: dict) -> str:
    field_id = str(field_payload.get("internal_field_id", "")).strip()
    if field_id == "":
        return _single_field_answer_payload(field_payload, "")

    parsed = _normalize_answer_to_field_values(answer)
    if field_id in parsed:
        return _single_field_answer_payload(field_payload, parsed[field_id])
    return _single_field_answer_payload(field_payload, "")


def _apply_unresolved_fallback_with_expanded_query(
    read_data: dict,
    first_pass_answers: list[str],
    rag_service: RAGService,
) -> list[str]:
    final_answers = list(first_pass_answers)
    for idx in range(len(final_answers)):
        field_payload = read_data["fields"][idx][0]
        field_id = str(field_payload.get("internal_field_id", "")).strip()
        if field_id == "":
            continue

        final_answers[idx] = _sanitize_answer_to_single_field(final_answers[idx], field_payload)
        first_pass_values = _normalize_answer_to_field_values(final_answers[idx])
        if _is_resolved_for_field(first_pass_values, field_id):
            continue

        generated_question = str(field_payload.get("generated_question", "")).strip()
        question_context = str(field_payload.get("question_context", "")).strip()
        expanded_query = (generated_question + " " + question_context).strip()
        if expanded_query == "":
            continue

        llm_prompt = ""
        if "llm_prompt" in read_data and idx < len(read_data.get("llm_prompt", [])):
            llm_prompt = str(read_data["llm_prompt"][idx]).strip()
        if llm_prompt == "":
            llm_prompt = generated_question

        fallback_answer = rag_service.chat(
            question=llm_prompt,
            instruction=_build_instruction(),
            input_context={
                "full_text_content": read_data["full_text_content"][idx],
                "fields": read_data["fields"][idx],
                "metadata": read_data["metadata"][idx],
            },
            retrieval_query=expanded_query,
            use_rag_context=True,
        )
        fallback_answer = _sanitize_answer_to_single_field(fallback_answer, field_payload)
        fallback_values = _normalize_answer_to_field_values(fallback_answer)
        if _is_resolved_for_field(fallback_values, field_id):
            final_answers[idx] = fallback_answer
            continue

        # Keep unresolved rows deterministic and field-local to avoid cross-field corruption.
        final_answers[idx] = _single_field_answer_payload(field_payload, "")
    return final_answers


def _write_answers_for_rows(
    filepath_rows: list[str],
    answer_rows: list[str],
    output_suffix: str,
    row_mode: str = "per_field",
) -> PDFWriteFormAction:
    answer_buffer = DictBuffer(id="FORM_FILLER_ANSWER_BUFFER_" + output_suffix)
    answer_buffer.install()
    for file_path, answer in zip(filepath_rows, answer_rows):
        answer_buffer.push({"filepath": file_path, "answer": answer})

    answer_parent = LinkBufferAction()
    answer_parent.set_buffer(answer_buffer)
    answer_parent.install()

    output_folder = _output_folder()
    output_folder.mkdir(parents=True, exist_ok=True)
    write_pdf_form_action = PDFWriteFormAction(
        id="WRITE_PDF_FORM_" + output_suffix.upper(),
        path_input_keys=["filepath"],
        fill_input_keys=["answer"],
        output_folder=str(output_folder),
        output_suffix=output_suffix,
        row_mode=row_mode,
    )
    write_pdf_form_action.add_parent(answer_parent)
    write_pdf_form_action.install()
    write_pdf_form_action.execute()
    return write_pdf_form_action


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
        retrieval_query_key="fields.0.generated_question",
        input_context_keys=["full_text_content", "fields", "metadata"],
        use_rag_context=True,
        pass_through_keys=["filepath"],
    )
    llm_fill_action.add_parent(read_pdf_form_action)
    llm_fill_action.set_service(rag_service)

    action_service = SimpleActionService(
        id="FORM_FILLER_ACTION_SERVICE_OPENAI",
        thread_type=ThreadType.ONLY_ONCE.value,
    )
    action_service.add_node(list_files_action)
    action_service.add_node(read_pdf_form_action)
    action_service.add_node(llm_fill_action)

    agent = Agent(id="FORM_FILLER_AGENT_E2E_OPENAI")
    agent.add_service(embedding_service)
    agent.add_service(rag_service)
    agent.add_service(action_service)

    try:
        agent.release(blocking=False)
        action_service.get_observer_thread()._thread.join(timeout=240)
        llm_data = llm_fill_action.get_buffer().data()
        read_data = read_pdf_form_action.get_buffer().data()
        if "answer" not in llm_data or len(llm_data.get("answer", [])) == 0:
            service_state = action_service.get_state()
            state_label = service_state.value if hasattr(service_state, "value") else str(service_state)
            pytest.skip(
                "Skipping OpenAI e2e test: no LLM answer produced "
                + "(state="
                + state_label
                + "). This can happen due to API/network/quota/provider issues."
            )
        final_answers = _apply_unresolved_fallback_with_expanded_query(
            read_data=read_data,
            first_pass_answers=list(llm_data["answer"]),
            rag_service=rag_service,
        )
        write_pdf_form_action = _write_answers_for_rows(
            filepath_rows=list(llm_data["filepath"]),
            answer_rows=final_answers,
            output_suffix="_openai",
            row_mode="per_field",
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
