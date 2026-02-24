import pytest


class DummyChain:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, payload, config=None):
        self.calls.append({"payload": payload, "config": config})
        return self.response


class DummyAIMessage:
    def __init__(self, content):
        self.content = content


def test_chat_uses_default_payload_values_when_optional_args_are_missing():
    """Ensure chat(question) keeps backward compatibility and fills default payload values."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs.retain_messages = False
    rs._langchain = DummyChain("ok")

    answer = rs.chat("What is RAG?")

    assert answer == "ok"
    assert len(rs._langchain.calls) == 1
    payload = rs._langchain.calls[0]["payload"]
    assert payload["question"] == "What is RAG?"
    assert payload["instruction"] == ""
    assert payload["input_context"] == ""
    assert payload["retrieval_query"] == "What is RAG?"
    assert payload["use_rag_context"] is True


def test_chat_passes_explicit_runtime_arguments_and_session_id():
    """Ensure explicit instruction/input_context/retrieval_query/use_rag_context/session_id are forwarded."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs.retain_messages = True
    rs._langchain = DummyChain("ok")

    answer = rs.chat(
        question="Fill fields",
        instruction="Return JSON only",
        input_context={"fields": [{"field_id": "kasse"}]},
        retrieval_query="insurance form policy",
        use_rag_context=False,
        session_id="S1",
    )

    assert answer == "ok"
    assert len(rs._langchain.calls) == 1
    payload = rs._langchain.calls[0]["payload"]
    config = rs._langchain.calls[0]["config"]
    assert payload["question"] == "Fill fields"
    assert payload["instruction"] == "Return JSON only"
    assert payload["input_context"] == '{"fields": [{"field_id": "kasse"}]}'
    assert payload["retrieval_query"] == "insurance form policy"
    assert payload["use_rag_context"] is False
    assert config == {"configurable": {"session_id": "S1"}}


def test_chat_raises_on_empty_question():
    """Ensure chat fails fast when question is empty."""
    from pydag.services.ServiceException import ServiceException
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs.retain_messages = False
    rs._langchain = DummyChain("ok")

    with pytest.raises(ServiceException):
        rs.chat("   ")


def test_chat_returns_message_content_for_non_string_llm_response():
    """Ensure chat returns .content when the underlying chain returns a message object."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs.retain_messages = False
    rs._langchain = DummyChain(DummyAIMessage("message-content"))

    answer = rs.chat("Q")

    assert answer == "message-content"


def test_chat_only_mode_works_without_retriever_or_embedding_folder_link():
    """Ensure chat-only mode works even if no retriever/embedding-store linkage is available."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs.retain_messages = False
    rs._retriever = None
    rs._langchain = DummyChain("chat-only-ok")

    answer = rs.chat(
        question="Answer from instruction only",
        instruction="Return a short answer.",
        use_rag_context=False,
    )

    assert answer == "chat-only-ok"
    assert len(rs._langchain.calls) == 1
    payload = rs._langchain.calls[0]["payload"]
    assert payload["question"] == "Answer from instruction only"
    assert payload["instruction"] == "Return a short answer."
    assert payload["input_context"] == ""
    assert payload["retrieval_query"] == "Answer from instruction only"
    assert payload["use_rag_context"] is False
