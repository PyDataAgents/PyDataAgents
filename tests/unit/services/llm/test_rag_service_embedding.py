import os
import sys
import types

import pytest

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

import pydag.services.llm.RAGService as rag_module
from pydag.services.llm.RAGService import RAGService


class DummyEmbeddingStore:
    def __init__(self):
        self.existing_ids = set()
        self.add_calls = []

    def get_by_ids(self, ids):
        return [ids[0]] if ids and ids[0] in self.existing_ids else []

    def add_documents(self, docs, ids=None):
        self.add_calls.append((docs, ids))
        if ids:
            self.existing_ids.update(ids)

    def as_retriever(self):
        class _Retriever:
            @staticmethod
            def get_relevant_documents(_question):
                return []

        return _Retriever()


class DummyLoader:
    def __init__(self, document_link, strategy="auto"):
        self.document_link = document_link
        self.strategy = strategy

    def load(self):
        return [
            f"chunk-0::{self.document_link}",
            f"chunk-1::{self.document_link}",
        ]


class DummySplitter:
    def __init__(self, chunk_size=500, chunk_overlap=100, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def split_documents(self, documents):
        return documents


def _build_service(monkeypatch):
    service = RAGService()
    service._embedding_store = DummyEmbeddingStore()
    monkeypatch.setattr(rag_module, "UnstructuredLoader", DummyLoader)
    monkeypatch.setattr(rag_module, "RecursiveCharacterTextSplitter", DummySplitter)
    monkeypatch.setattr(rag_module, "filter_complex_metadata", lambda documents: documents)
    return service


def test_add_document_skips_non_text_file(tmp_path, monkeypatch):
    """Ensure non-text files are ignored and not inserted into the embedding store."""
    service = _build_service(monkeypatch)

    image_file = tmp_path / "image.png"
    image_file.write_bytes(b"not-text")

    service.add_document(str(image_file))

    assert len(service._embedding_store.add_calls) == 0
    assert str(image_file) not in service.document_links


def test_add_document_skips_duplicate_document(tmp_path, monkeypatch):
    """Ensure already-indexed documents are skipped based on the *_0 id probe."""
    service = _build_service(monkeypatch)

    text_file = tmp_path / "test.txt"
    text_file.write_text("hello", encoding="utf-8")
    service._embedding_store.existing_ids.add(str(text_file) + "_0")

    service.add_document(str(text_file))

    assert len(service._embedding_store.add_calls) == 0


def test_add_document_stores_chunk_ids_with_document_prefix(tmp_path, monkeypatch):
    """Ensure added chunk ids use the '<document_link>_<index>' naming scheme."""
    service = _build_service(monkeypatch)

    text_file = tmp_path / "manual.txt"
    text_file.write_text("hello", encoding="utf-8")

    service.add_document(str(text_file))

    assert len(service._embedding_store.add_calls) == 1
    _, ids = service._embedding_store.add_calls[0]
    assert ids == [str(text_file) + "_0", str(text_file) + "_1"]


def test_add_documents_scans_folders_recursively_and_embeds_only_text(tmp_path, monkeypatch):
    """Ensure recursive folder ingestion embeds text files and skips non-text files."""
    service = _build_service(monkeypatch)

    root_folder = tmp_path / "docs"
    nested_folder = root_folder / "nested"
    nested_folder.mkdir(parents=True)

    file_a = root_folder / "a.txt"
    file_b = nested_folder / "b.txt"
    file_c = nested_folder / "skip.png"

    file_a.write_text("text-a", encoding="utf-8")
    file_b.write_text("text-b", encoding="utf-8")
    file_c.write_bytes(b"image")

    service.add_documents(str(root_folder))

    all_ids = []
    for _, ids in service._embedding_store.add_calls:
        all_ids.extend(ids)

    assert any(id_value.startswith(str(file_a) + "_") for id_value in all_ids)
    assert any(id_value.startswith(str(file_b) + "_") for id_value in all_ids)
    assert not any(id_value.startswith(str(file_c) + "_") for id_value in all_ids)


def test_on_start_uses_existing_vector_store_and_appends_document_links(tmp_path, monkeypatch):
    """Ensure startup opens an existing vector store path and appends configured documents."""
    class DummySentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name

        def save(self, _path):
            return

    class DummyChroma:
        instances = []

        def __init__(self, persist_directory=None, embedding_function=None):
            self.persist_directory = persist_directory
            self.embedding_function = embedding_function
            self.existing_ids = set()
            self.add_calls = []
            DummyChroma.instances.append(self)

        def get_by_ids(self, ids):
            return [ids[0]] if ids and ids[0] in self.existing_ids else []

        def add_documents(self, docs, ids=None):
            self.add_calls.append((docs, ids))
            if ids:
                self.existing_ids.update(ids)

        def as_retriever(self):
            class _Retriever:
                @staticmethod
                def get_relevant_documents(_question):
                    return []

            return _Retriever()

    monkeypatch.setattr(rag_module, "SentenceTransformer", DummySentenceTransformer)
    monkeypatch.setattr(rag_module, "HuggingFaceEmbeddings", lambda model_name: {"model_name": model_name})
    monkeypatch.setattr(rag_module, "Chroma", DummyChroma)
    monkeypatch.setattr(rag_module, "UnstructuredLoader", DummyLoader)
    monkeypatch.setattr(rag_module, "RecursiveCharacterTextSplitter", DummySplitter)
    monkeypatch.setattr(rag_module, "filter_complex_metadata", lambda documents: documents)
    monkeypatch.setattr(RAGService, "_create_llm_and_chain", lambda self: None)

    store_folder = tmp_path / "store"
    store_folder.mkdir(parents=True)
    store_db_file = store_folder / "chroma.sqlite3"
    store_db_file.write_text("", encoding="utf-8")

    text_file = tmp_path / "doc.txt"
    text_file.write_text("hello", encoding="utf-8")

    service = RAGService(
        vector_store_path=str(store_db_file),
        document_links=[str(text_file)],
        model_provider="OLLAMA",
        model="dummy",
    )
    service._on_start()

    assert len(DummyChroma.instances) == 1
    chroma_instance = DummyChroma.instances[0]
    assert os.path.normpath(chroma_instance.persist_directory) == os.path.normpath(str(store_folder))
    assert len(chroma_instance.add_calls) == 1

    _, ids = chroma_instance.add_calls[0]
    assert ids == [str(text_file) + "_0", str(text_file) + "_1"]
