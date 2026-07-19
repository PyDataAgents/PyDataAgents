import configparser
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

from pydag.nodes.llm.LLMChatAction import LLMChatAction
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


def test_llm_chat_action_reads_local_image_context_from_path():
    """Ensure LLMChatAction can answer a question from a local image path."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping live LLMChatAction image-context test: missing OPENAI_API_KEY in [OPENAI] of config.ini")

    image_path = _image_file()
    assert image_path.is_file()

    service = _OpenAIChatOnlyRAGService(
        id="RAG_IMAGE_CONTEXT_OPENAI",
        api_key=config["OPENAI"]["OPENAI_API_KEY"],
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
            context_files_value=str(image_path),
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
