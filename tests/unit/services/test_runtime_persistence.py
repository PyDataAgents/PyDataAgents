from __future__ import annotations

from dataclasses import dataclass, field
import shutil
from pathlib import Path
import uuid

import pytest

from pydag.agents.Agent import Agent
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.RuntimeStorage import CheckpointManifest, CheckpointReason, RuntimeStorage

import importlib


def _workspace_temp_dir(name: str) -> Path:
    path = Path("resources") / "tmp-tests" / name / uuid.uuid4().hex[:8]
    path.mkdir(parents=True, exist_ok=True)
    return path


def _import_or_skip(module_name: str, reason: str):
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"{reason}: {exc}")


def test_agent_config_uses_central_resource_roots():
    AgentConfig.ensure_resource_layout()

    assert AgentConfig.RUNTIME_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "runtime"
    assert AgentConfig.INPUT_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "inputs"
    assert AgentConfig.MODEL_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "models"
    assert AgentConfig.EMBEDDING_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "embeddings"
    assert AgentConfig.OUTPUT_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "outputs"
    assert AgentConfig.SCRIPT_RESOURCE_ROOT == AgentConfig.RESOURCE_ROOT / "scripts"
    assert AgentConfig.RUNTIME_RESOURCE_ROOT.exists()
    assert AgentConfig.MODEL_RESOURCE_ROOT.exists()
    assert AgentConfig.EMBEDDING_RESOURCE_ROOT.exists()
    assert AgentConfig.OUTPUT_RESOURCE_ROOT.exists()


def test_rag_and_file_embedding_services_resolve_central_resource_roots():
    RAGService = _import_or_skip(
        "pydag.services.llm.RAGService",
        "RAG runtime tests require importable embedding dependencies",
    ).RAGService
    FileEmbeddingService = _import_or_skip(
        "pydag.services.documents.FileEmbeddingService",
        "File embedding runtime tests require importable embedding dependencies",
    ).FileEmbeddingService
    agent = Agent(id="AG_SERVICE_RUNTIME")
    rag = RAGService(id="RAG_DEFAULT_STORE", model_provider="OLLAMA", model="dummy")
    embedding = FileEmbeddingService(store_name="test-store")

    try:
        rag.install(agent)
        embedding.install(agent)

        rag_directory = Path(rag._resolve_vector_store_directory())
        embedding_directory = Path(embedding._resolve_store_directory())
        standalone_embedding = FileEmbeddingService(id="EMBED_STANDALONE_COMPARE", store_name="test-store")
        standalone_directory = Path(standalone_embedding._resolve_store_directory())

        assert rag_directory == AgentConfig.EMBEDDING_RESOURCE_ROOT / "service-rag-default-store"
        assert embedding_directory == AgentConfig.EMBEDDING_RESOURCE_ROOT / "test-store"
        assert embedding_directory == standalone_directory
    finally:
        rag.uninstall(agent)
        embedding.uninstall(agent)
        shutil.rmtree(agent._runtime_storage.runtime_root, ignore_errors=True)


def test_file_embedding_service_uses_central_path_when_standalone():
    FileEmbeddingService = _import_or_skip(
        "pydag.services.documents.FileEmbeddingService",
        "File embedding runtime tests require importable embedding dependencies",
    ).FileEmbeddingService
    service = FileEmbeddingService(id="EMBED_STANDALONE", store_name="standalone-store")
    assert Path(service._resolve_store_directory()) == AgentConfig.EMBEDDING_RESOURCE_ROOT / "standalone-store"


def test_rag_service_relative_vector_store_path_uses_central_embedding_scope():
    RAGService = _import_or_skip(
        "pydag.services.llm.RAGService",
        "RAG runtime tests require importable embedding dependencies",
    ).RAGService
    agent = Agent(id="AG_RAG_RELATIVE_STORE")
    rag = RAGService(model_provider="OLLAMA", model="dummy", persist_directory="team-store")

    try:
        rag.install(agent)
        assert Path(rag._resolve_vector_store_directory()) == AgentConfig.EMBEDDING_RESOURCE_ROOT / "team-store"
    finally:
        rag.uninstall(agent)
        shutil.rmtree(agent._runtime_storage.runtime_root, ignore_errors=True)


def test_rag_and_file_embedding_services_prefer_restored_runtime_store_directories():
    RAGService = _import_or_skip(
        "pydag.services.llm.RAGService",
        "RAG runtime tests require importable embedding dependencies",
    ).RAGService
    FileEmbeddingService = _import_or_skip(
        "pydag.services.documents.FileEmbeddingService",
        "File embedding runtime tests require importable embedding dependencies",
    ).FileEmbeddingService

    rag = RAGService(model_provider="OLLAMA", model="dummy")
    embedding = FileEmbeddingService(store_name="test-store")
    rag._resolved_vector_store_directory = "restored/rag-store"
    embedding._resolved_store_directory = "restored/embed-store"

    assert rag._resolve_vector_store_directory() == "restored/rag-store"
    assert embedding._resolve_store_directory() == "restored/embed-store"


def test_llm_service_rebuild_runtime_handles_restores_session_histories(monkeypatch):
    module = _import_or_skip(
        "pydag.services.llm.LLMService",
        "LLM runtime tests require importable LangChain dependencies",
    )
    chat_module = _import_or_skip(
        "langchain_core.chat_history",
        "LLM runtime tests require importable LangChain chat history dependencies",
    )
    messages_module = _import_or_skip(
        "langchain_core.messages",
        "LLM runtime tests require importable LangChain message dependencies",
    )
    LLMService = module.LLMService
    InMemoryChatMessageHistory = chat_module.InMemoryChatMessageHistory
    HumanMessage = messages_module.HumanMessage

    class FakePrompt:
        def __or__(self, other):
            return {"llm": other}

    class FakeChatPromptTemplate:
        @staticmethod
        def from_messages(messages):
            return FakePrompt()

    class FakeRunnableWithMessageHistory:
        def __init__(self, chain, **kwargs):
            self.chain = chain
            self.kwargs = kwargs

    monkeypatch.setattr(module, "ChatPromptTemplate", FakeChatPromptTemplate)
    monkeypatch.setattr(module, "RunnableWithMessageHistory", FakeRunnableWithMessageHistory)
    monkeypatch.setattr(LLMService, "_create_llm", lambda self: setattr(self, "_llm", object()))

    service = LLMService(retain_messages=True, api_key="test-key", model_provider="OPENAI")
    history = InMemoryChatMessageHistory()
    history.add_message(HumanMessage(content="hello"))
    service._session_histories["session-1"] = history
    snapshot = service.checkpoint().to_dict()

    clone = LLMService(retain_messages=True, api_key="test-key", model_provider="OPENAI", uid=service.uid)
    assert clone.restore(snapshot) is True
    assert "session-1" in clone._session_histories
    assert clone._session_histories["session-1"].messages[0].content == "hello"
    assert clone._llm is not None
    assert clone._langchain is not None


def test_rest_service_rebuild_runtime_handles_recreates_fastapi_app():
    RestService = _import_or_skip(
        "pydag.services.rest.RestService",
        "Rest service runtime tests require importable FastAPI dependencies",
    ).RestService
    agent = Agent(id="AG_REST_RUNTIME")
    service = RestService(id="REST_RUNTIME")

    try:
        service.install(agent)
        assert service._app is not None

        service._app = None
        service.rebuild_runtime_handles(agent)

        assert service._app is not None
    finally:
        service.uninstall(agent)
        shutil.rmtree(agent._runtime_storage.runtime_root, ignore_errors=True)


def test_datamodel_service_snapshot_restore_roundtrip():
    DataModelService = _import_or_skip(
        "pydag.services.datamodel.DataModelService",
        "DataModelService runtime tests require an importable pandas/numpy stack",
    ).DataModelService
    temp_dir = _workspace_temp_dir("datamodel-runtime")
    model_file = temp_dir / "TempModel.py"
    model_file.write_text(
        "\n".join(
            [
                "from dataclasses import dataclass, field",
                "from pydag.services.datamodel.DataModel import DataModel",
                "",
                "@dataclass",
                "class TempModel(DataModel):",
                "    a: float = field(default=None, metadata={'description': 'a'})",
                "    b: float = field(default=None, metadata={'description': 'b'})",
                "",
                "    def compute(self):",
                "        self.b = self.a * 2",
            ]
        ),
        encoding="utf-8",
    )

    service = DataModelService(model_path=str(model_file), model_name="TempModel")
    clone = DataModelService(model_path=str(model_file), model_name="TempModel")

    try:
        service.install()
        service.updates("model-1", {"a": 3})
        snapshot = service.checkpoint().to_dict()

        clone.install()
        assert clone.restore(snapshot) is True
        restored_model = clone.get_data_model("model-1")

        assert restored_model is not None
        assert restored_model.to_dict(with_hidden=True) == {"a": 3, "b": 6}
    finally:
        service.uninstall()
        clone.uninstall()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_runtime_storage_manifest_roundtrip_keeps_extended_checkpoint_metadata():
    storage = RuntimeStorage(agent_uid=f"runtime-meta-{uuid.uuid4().hex[:8]}")
    storage.ensure_layout()
    manifest = CheckpointManifest(
        checkpoint_id="checkpoint-meta",
        agent_uid=storage.agent_uid,
        agent_id="AG_META",
        created_at=123,
        lifecycle_state="RUNNING",
        run_id="run-1",
        checkpoint_reason=CheckpointReason.MANUAL.value,
        agent_type="Agent",
        agent_config_fingerprint="config-fp",
        agent_definition_fingerprint="definition-fp",
        element_files={"buffer/buf-1": "elements/buffer.json"},
        element_inventory={
            "buffer/buf-1": {
                "uid": "buffer/buf-1",
                "definition_fingerprint": "element-fp",
                "type": "pydag.buffers.DictBuffer",
            }
        },
        metadata={"note": "extended"},
    )

    try:
        storage.write_manifest(manifest)
        loaded = storage.load_manifest("checkpoint-meta")

        assert loaded["checkpoint_reason"] == CheckpointReason.MANUAL.value
        assert loaded["agent_type"] == "Agent"
        assert loaded["agent_config_fingerprint"] == "config-fp"
        assert loaded["agent_definition_fingerprint"] == "definition-fp"
        assert loaded["element_inventory"]["buffer/buf-1"]["definition_fingerprint"] == "element-fp"
    finally:
        shutil.rmtree(storage.runtime_root, ignore_errors=True)
