from pathlib import Path

import pytest
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


class RecordingVectorStore(VectorStore):
    def __init__(self):
        self.queries = []
        self.texts = []

    def add_texts(self, texts, metadatas=None, ids=None, **kwargs):
        self.texts.extend(texts)
        return ids or [str(i) for i, _ in enumerate(texts)]

    def similarity_search(self, query: str, k: int = 4, **kwargs):
        self.queries.append(query)
        return [
            Document(page_content="first retrieved chunk"),
            Document(page_content="second retrieved chunk"),
        ][:k]

    @classmethod
    def from_texts(cls, texts, embedding, metadatas=None, ids=None, **kwargs):
        store = cls()
        store.add_texts(texts, metadatas=metadatas, ids=ids, **kwargs)
        return store


class RecordingEmbeddingStore:
    def __init__(self):
        self.existing_ids = set()
        self.get_by_ids_calls = []
        self.add_documents_calls = []

    def get_by_ids(self, ids):
        self.get_by_ids_calls.append(ids)
        return [id_value for id_value in ids if id_value in self.existing_ids]

    def add_documents(self, documents, ids=None):
        self.add_documents_calls.append((documents, ids))
        if ids:
            self.existing_ids.update(ids)


class KeywordPdfVectorStore(VectorStore):
    def __init__(self, documents):
        self.documents = documents
        self.queries = []

    def add_texts(self, texts, metadatas=None, ids=None, **kwargs):
        self.documents.extend(Document(page_content=text) for text in texts)
        return ids or [str(i) for i, _ in enumerate(texts)]

    def similarity_search(self, query: str, k: int = 4, **kwargs):
        self.queries.append(query)
        query_terms = [term.lower() for term in str(query).split() if term.strip()]

        def score(doc):
            text = doc.page_content.lower()
            return sum(text.count(term) for term in query_terms)

        ranked_docs = sorted(self.documents, key=score, reverse=True)
        return ranked_docs[:k]

    @classmethod
    def from_texts(cls, texts, embedding, metadatas=None, ids=None, **kwargs):
        return cls([Document(page_content=text) for text in texts])


@pytest.fixture(scope="module")
def pdf_vector_store():
    pytest.importorskip("pypdf")
    from pydag.services.llm.RAGService import RAGService

    pdf_path = (
        Path(__file__).parents[1]
        / "documents"
        / "test_documents_for_embedding"
        / "docs_5"
        / "2210.03629v3.pdf"
    )
    documents = RAGService()._load_documents(str(pdf_path))
    split_docs = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""],
    ).split_documents(documents)

    assert any(
        "Angeliki" in doc.page_content and "Lazaridou" in doc.page_content
        for doc in split_docs
    )
    return KeywordPdfVectorStore(split_docs)


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


def test_get_retrieved_context_text_invokes_langchain_retriever_with_stringified_retrieval_query(monkeypatch):
    """Ensure retrieval calls LangChain's VectorStoreRetriever API with str(retrieval_query)."""
    from pydag.services.llm.RAGService import RAGService

    langchain_calls = []
    original_invoke = VectorStoreRetriever.invoke

    def recording_invoke(self, query, *args, **kwargs):
        langchain_calls.append(query)
        return original_invoke(self, query, *args, **kwargs)

    monkeypatch.setattr(
        VectorStoreRetriever,
        "invoke",
        recording_invoke,
    )

    rs = RAGService()
    vector_store = RecordingVectorStore()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    rs._retriever = retriever

    context = rs._get_retrieved_context_text(retrieval_query=12345)

    assert langchain_calls == ["12345"]
    assert vector_store.queries == ["12345"]
    assert context == "first retrieved chunk\n\nsecond retrieved chunk"


def test_load_documents_uses_real_unstructured_loader_for_text_file(tmp_path):
    """Ensure non-PDF documents still use the real UnstructuredLoader path."""
    from pydag.services.llm.RAGService import RAGService

    text_file = tmp_path / "rag_context.txt"
    text_file.write_text(
        "RAGService UnstructuredLoader integration test content.",
        encoding="utf-8",
    )

    documents = RAGService()._load_documents(str(text_file))

    assert any(
        "UnstructuredLoader integration test content" in doc.page_content
        for doc in documents
    )


def test_load_documents_reads_existing_pdf_without_unstructured_loader(monkeypatch):
    """Ensure local PDFs use the pypdf path instead of UnstructuredLoader's PDF partitioner."""
    import pydag.services.llm.RAGService as rag_module
    from pydag.services.llm.RAGService import RAGService

    def fail_if_unstructured_loader_is_used(*_args, **_kwargs):
        raise AssertionError("PDF loading should not call UnstructuredLoader")

    monkeypatch.setattr(
        rag_module,
        "UnstructuredLoader",
        fail_if_unstructured_loader_is_used,
    )
    pdf_path = (
        Path(__file__).parents[1]
        / "documents"
        / "test_documents_for_embedding"
        / "docs_5"
        / "2210.03629v3.pdf"
    )

    documents = RAGService()._load_documents(str(pdf_path))

    assert any(
        "Angeliki" in doc.page_content and "Lazaridou" in doc.page_content
        for doc in documents
    )


def test_add_document_does_not_index_same_document_twice(tmp_path):
    """Ensure add_document skips a document after its first chunk id already exists."""
    from pydag.services.llm.RAGService import RAGService

    text_file = tmp_path / "duplicate-source.txt"
    text_file.write_text(
        "This document should be loaded once and indexed only once.",
        encoding="utf-8",
    )

    service = RAGService()
    embedding_store = RecordingEmbeddingStore()
    service._embedding_store = embedding_store

    service.add_document(str(text_file))
    service.add_document(str(text_file))

    expected_probe_id = str(text_file) + "_0"
    assert embedding_store.get_by_ids_calls == [
        [expected_probe_id],
        [expected_probe_id],
    ]
    assert len(embedding_store.add_documents_calls) == 1
    _, indexed_ids = embedding_store.add_documents_calls[0]
    assert indexed_ids == [expected_probe_id]
    assert service.document_links == [str(text_file)]


def test_get_retrieved_context_text_retrieves_expected_context_from_existing_pdf(pdf_vector_store):
    """Ensure RAGService retrieves relevant context from an existing PDF fixture."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs._retriever = pdf_vector_store.as_retriever(search_kwargs={"k": 3})

    context = rs._get_retrieved_context_text("Angeliki Lazaridou")

    assert pdf_vector_store.queries[-1] == "Angeliki Lazaridou"
    assert "Angeliki Lazaridou" in " ".join(context.split())


def test_get_retrieved_context_text_skips_existing_pdf_retriever_when_rag_context_is_disabled(pdf_vector_store):
    """Ensure disabled RAG context does not query the PDF-backed retriever."""
    from pydag.services.llm.RAGService import RAGService

    rs = RAGService()
    rs._retriever = pdf_vector_store.as_retriever(search_kwargs={"k": 3})
    calls_before = list(pdf_vector_store.queries)

    context = rs._get_retrieved_context_text(
        retrieval_query="Angeliki Lazaridou",
        use_rag_context=False,
    )

    assert context == ""
    assert pdf_vector_store.queries == calls_before
