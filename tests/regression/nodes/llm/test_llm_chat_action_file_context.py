import configparser
import os
from pathlib import Path
import sys
import types

import pytest
from langchain_openai import ChatOpenAI

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
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.llm.RAGService import RAGService


class _OpenAIChatOnlyRAGService(RAGService):
    """OpenAI-backed RAGService variant without embedding/retriever startup."""

    def _on_start(self):
        self._retriever = None
        self._embedding_store = None
        self._embedding_model = None
        self._create_llm()

    def _create_llm(self):
        self._llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key, temperature=0)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _image_file() -> Path:
    return _repo_root() / "tests" / "unit" / "nodes" / "llm" / "cyber_cat_christmas.jpg"


def _relative_image_file() -> str:
    return os.path.relpath(_image_file(), Path.cwd())


def _openai_api_key() -> str:
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping live LLMChatAction image-context test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    return config["OPENAI"]["OPENAI_API_KEY"]


def _link_parent_with_row(row: dict) -> LinkBufferAction:
    parent_buf = DictBuffer(id="PARENT_IMAGE_CONTEXT_BUF")
    parent_buf.install()
    parent_buf.push({key: [value] for key, value in row.items()})

    parent_link = LinkBufferAction(id="PARENT_IMAGE_CONTEXT_LINK")
    parent_link.set_buffer(parent_buf)
    parent_link.install()
    return parent_link


def test_llm_chat_action_reads_local_image_context_from_path():
    """Ensure LLMChatAction can answer a question from a local image path."""
    image_path = _image_file()
    relative_image_path = _relative_image_file()
    assert image_path.is_file()
    assert not os.path.isabs(relative_image_path)

    service = _OpenAIChatOnlyRAGService(
        id="RAG_IMAGE_CONTEXT_OPENAI",
        api_key=_openai_api_key(),
        model_provider="OPENAI",
        model="gpt-4.1-mini",
        retain_messages=False,
    )
    service.install()
    service.start()
    try:
        chat_action = LLMChatAction(
            id="LLM_IMAGE_CONTEXT_ACTION",
            question_value=(
                "Look at the supplied image and answer exactly one lowercase English word, "
                "with no punctuation: what animal is shown?"
            ),
            instruction_value="Use the image context. Return only the animal name.",
            context_files_value=relative_image_path,
            use_rag_context=False,
        )
        chat_action.set_service(service)
        chat_action.install()
        chat_action.execute()

        output = chat_action.get_buffer().data()
        answers = output.get("answer", [])
        assert len(answers) == 1
        answer = str(answers[0]).strip().lower()
        assert "cat" in answer, "Expected the image context to identify a cat, got: " + answer
    finally:
        service.stop()


def test_llm_chat_action_accepts_parent_key_file_references_with_image_files():
    """Ensure parent-key file references can be used as input context and file context."""
    image_path = _image_file()
    relative_image_path = _relative_image_file()
    assert image_path.is_file()
    assert not os.path.isabs(relative_image_path)

    row = {
        "question": (
            "Look at the supplied image files and answer exactly one lowercase English word, "
            "with no punctuation: what animal is shown?"
        ),
        "key1": relative_image_path,
        "key2": image_path.as_uri(),
        "key3": [relative_image_path, image_path.as_uri()],
    }

    service = _OpenAIChatOnlyRAGService(
        id="RAG_PARENT_KEY_IMAGE_CONTEXT_OPENAI",
        api_key=_openai_api_key(),
        model_provider="OPENAI",
        model="gpt-4.1-mini",
        retain_messages=False,
    )
    service.install()
    service.start()
    try:
        chat_action = LLMChatAction(
            id="LLM_PARENT_KEY_IMAGE_CONTEXT_ACTION",
            question_key="question",
            instruction_value="Use the image file context. Return only the animal name.",
            input_context_keys=["key1", "key2", "key3"],
            context_files_key="key3",
            use_rag_context=False,
        )
        chat_action.set_service(service)
        chat_action.add_parent(_link_parent_with_row(row))
        chat_action.install()
        chat_action.execute()

        output = chat_action.get_buffer().data()
        answers = output.get("answer", [])
        assert len(answers) == 1
        answer = str(answers[0]).strip().lower()
        assert "cat" in answer, "Expected parent-key file-reference call to identify a cat, got: " + answer
    finally:
        service.stop()


def test_llm_chat_action_accepts_nested_file_reference_input_context_with_image_files():
    """Ensure nested file-reference input context can be used together with real file context."""
    image_path = _image_file()
    relative_image_path = _relative_image_file()
    assert image_path.is_file()
    assert not os.path.isabs(relative_image_path)

    nested_context = {
        "file1": relative_image_path,
        "file2": image_path.as_uri(),
        "file3": [relative_image_path, image_path.as_uri()],
    }
    context_files = [
        nested_context["file1"],
        nested_context["file2"],
        *nested_context["file3"],
    ]

    service = _OpenAIChatOnlyRAGService(
        id="RAG_NESTED_IMAGE_CONTEXT_OPENAI",
        api_key=_openai_api_key(),
        model_provider="OPENAI",
        model="gpt-4.1-mini",
        retain_messages=False,
    )
    service.install()
    service.start()
    try:
        chat_action = LLMChatAction(
            id="LLM_NESTED_IMAGE_CONTEXT_ACTION",
            question_value=(
                "Look at the supplied image files and answer exactly one lowercase English word, "
                "with no punctuation: what animal is shown?"
            ),
            instruction_value="Use the image file context. Return only the animal name.",
            input_context_value=nested_context,
            context_files_value=context_files,
            use_rag_context=False,
        )
        chat_action.set_service(service)
        chat_action.install()
        chat_action.execute()

        output = chat_action.get_buffer().data()
        answers = output.get("answer", [])
        assert len(answers) == 1
        answer = str(answers[0]).strip().lower()
        assert "cat" in answer, "Expected nested file-reference call to identify a cat, got: " + answer
    finally:
        service.stop()
