from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import ClassVar
from loguru import logger
from langchain_chroma import Chroma
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from ...agents.AgentConfig import AgentConfig
from ...agents.AgentElement import artifact_descriptor_field, runtime_handle_field
from ...agents.RuntimeStorage import ArtifactPolicy, normalize_runtime_key
from ..Service import Service
from ..ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ...utils.ModelUtils import ModelUtils

@dataclass
class FileEmbeddingService(Service):
    """File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.
    """
    NON_TEXT_EXTENSIONS: ClassVar[set[str]] = FileUtils.COMMON_NON_TEXT_EXTENSIONS | {".db"}
    
    docs_folder : list[str] | str = field(default=None, metadata={"description": "Folder links to load documents from into embedded store on startup"})
    embedding_model_name : str = field(default="all-MiniLM-L6-v2", metadata={"description": "name of the embedding model to use for embedding store. Currently, only sentence transformer models are supported, e.g. all-MiniLM-L6-v2. See "})
    store_name : str = field(default=None, metadata={"description": "name of the embedded store"})
    _embedding_store : object = runtime_handle_field(default=None, init=False, repr=False)
    _embedding_model : object = runtime_handle_field(default=None, init=False, repr=False)
    _retriever : object = runtime_handle_field(default=None, init=False, repr=False)
    _resolved_store_directory : str | None = artifact_descriptor_field(
        default=None,
        init=False,
        repr=False,
        name="embedding_store",
        kind="vector_store",
        policy=ArtifactPolicy.DURABLE.value,
    )
            
    def _on_start(self):
        self.rebuild_runtime_handles()

    def rebuild_runtime_handles(self, agent=None):
        if self._embedding_model is not None and self._embedding_store is not None:
            return
        runtime_agent = agent if agent is not None else getattr(self, "_agent", None)
        model_resource_root = self._resolve_model_resource_root(runtime_agent)
        model_artifact_path = self._resolve_model_artifact_path(runtime_agent)
        self._resolved_store_directory = self._resolve_store_directory(runtime_agent)
        self.clear_registered_artifacts()
        self.register_artifact(
            name="embedding_model",
            path=str(model_artifact_path),
            kind="model_cache",
            policy=ArtifactPolicy.SHARED.value,
            metadata={"embedding_model_name": self.embedding_model_name},
        )
        self.register_artifact(
            name="embedding_store",
            path=self._resolved_store_directory,
            kind="vector_store",
            policy=ArtifactPolicy.DURABLE.value,
            metadata={"embedding_model_name": self.embedding_model_name, "store_name": self.store_name},
        )
        self._embedding_model = ModelUtils.build_huggingface_embeddings(model_resource_root, self.embedding_model_name)
        self._embedding_store = Chroma(
            persist_directory=self._resolved_store_directory,
            embedding_function=self._embedding_model,
        )
        logger.debug("created embedding store with embedding model " + self.embedding_model_name)
        if isinstance(self.docs_folder, str):
            self.docs_folder = [self.docs_folder]
        if self.docs_folder is None or len(self.docs_folder) == 0:
            logger.warning("No folders provided for embedding. Please provide at least one valid folder path to load documents from.")
            raise ServiceException("No folders provided for embedding. Please provide at least one valid folder path to load documents from.")    

        for _docs_folder in self.docs_folder:
            _docs_folder = os.path.join(_docs_folder) # ensure that folder path is in correct format for current operating system
            if not os.path.exists(_docs_folder) or not os.path.isdir(_docs_folder):
                print(f"The folder: {_docs_folder} is not valid. Please provide a valid folder path to load documents from.")
                raise ServiceException(f"The folder: {_docs_folder} is not valid. Please provide a valid folder path to load documents from.")
            else:
                _documents = os.listdir(_docs_folder)
                if len(_documents) == 0:
                    logger.warning(f"The folder: {_docs_folder} is empty. Please provide a folder with valid documents to load.")
                    continue
                for _doc in _documents:
                    document_link = _docs_folder + os.sep + _doc
                    self.add_document(document_link)

    
    def _on_stop(self):
        self._langchain = None
        self._embedding_store = None
        self._embedding_model = None
        self._retriever = None

    def _resolve_model_resource_root(self, agent=None) -> Path:
        AgentConfig.ensure_resource_layout()
        return AgentConfig.MODEL_RESOURCE_ROOT

    def _resolve_model_artifact_path(self, agent=None) -> Path:
        return self._resolve_model_resource_root(agent) / self.embedding_model_name
    
    def add_document(self, document_link):
        # Check if document already in embedding store
        if self._embedding_store.get_by_ids([document_link + "_0"]): # check if document with id of document link + "_0" exists in embedding store, if yes, assume that all chunks of the document are already embedded and skip embedding for this document
            logger.debug("document " + document_link + " already embedded in embedding store, skipping embedding for this document")
            return
        # Only allow embedding of text-based documents, skip non-text files based on file extension to avoid unwanted OCR/Tesseract triggers and to save resources. This is a simple heuristic and can be further improved by actually checking the file type or content instead of just relying on the file extension, but it should work well in most cases and is much more efficient than trying to load every file and checking its content.
        if os.path.splitext(document_link)[1].lower() in self.NON_TEXT_EXTENSIONS:
            logger.warning("skipping non-text file " + document_link + " for embedding")
            return
        loader = UnstructuredLoader(document_link, strategy="auto") 
        documents = loader.load()
        # filter for complex data        
        filtered_docs = filter_complex_metadata(documents) # Filter out documents with complex metadata that cannot be processed by the embedding model
        # Split into chunks
        # This is generally more "intelligent" than CharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=250,
            separators=["\n\n", "\n", " ", ""]
        )
        split_docs = text_splitter.split_documents(filtered_docs)
        self._embedding_store.add_documents(split_docs, ids=[document_link + "_" + str(i) for i in range(len(split_docs))]) # add document link as prefix to the id of the embedded document to ensure uniqueness and to be able to identify the source document of the embedded chunk later on when retrieving relevant documents from the embedding store
        logger.debug("embedded document " + document_link + " into embedding store")

    def _resolve_store_directory(self, agent=None) -> str:
        if self._resolved_store_directory:
            return self._resolved_store_directory
        AgentConfig.ensure_resource_layout()
        if self.store_name is None:
            store_root = AgentConfig.EMBEDDING_RESOURCE_ROOT / normalize_runtime_key(
                self.uid, fallback="embedding-store"
            )
            FileUtils.create_dir(str(store_root))
            return str(store_root)
        store_key = normalize_runtime_key(self.store_name, fallback="embedding-store")
        store_root = AgentConfig.EMBEDDING_RESOURCE_ROOT / store_key
        FileUtils.create_dir(str(store_root))
        return str(store_root)
