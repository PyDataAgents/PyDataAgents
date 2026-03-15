from __future__ import annotations

from dataclasses import dataclass, field
import shutil
from pathlib import Path
import uuid

from pydag.agents.Agent import Agent
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.services.documents.FileEmbeddingService import FileEmbeddingService
from pydag.services.llm.RAGService import RAGService


def _workspace_temp_dir(name: str) -> Path:
    path = Path("resources") / "tmp-tests" / name / uuid.uuid4().hex[:8]
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_rag_and_file_embedding_services_resolve_runtime_artifact_roots_when_installed():
    agent = Agent(id="AG_SERVICE_RUNTIME")
    rag = RAGService(model_provider="OLLAMA", model="dummy")
    embedding = FileEmbeddingService(store_name="test-store")

    try:
        rag.install(agent)
        embedding.install(agent)

        rag_directory = Path(rag._resolve_vector_store_directory())
        embedding_directory = Path(embedding._resolve_store_directory())
        legacy_directory = Path(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER) / "test-store"

        assert rag_directory == rag.get_artifact_root(agent) / "vector_store"
        assert embedding_directory == embedding.get_artifact_root(agent) / "vector_store"
        assert embedding_directory != legacy_directory
    finally:
        rag.uninstall(agent)
        embedding.uninstall(agent)
        shutil.rmtree(agent._runtime_storage.runtime_root, ignore_errors=True)


def test_file_embedding_service_keeps_legacy_path_when_standalone():
    service = FileEmbeddingService(store_name="legacy-store")
    assert Path(service._resolve_store_directory()) == Path(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER) / "legacy-store"


def test_datamodel_service_snapshot_restore_roundtrip():
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
