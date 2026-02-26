from dataclasses import dataclass, field
import os
from pathlib import Path
from loguru import logger
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores.utils import filter_complex_metadata
from ...agents.AgentConfig import AgentConfig
from ..Service import Service
from ..ServiceException import ServiceException

@dataclass
class FileEmbeddingService(Service):
    """File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.
    """
    
    # Constants
    MODEL_RESOURCE_FOLDER = Path(AgentConfig.MODEL_RESOURCE_FOLDER)
    EMBEDDINGS_RESOURCE_FOLDER = Path(AgentConfig.EMBEDDINGS_RESOURCE_FOLDER)
    
    docs_folder : list[str] | str = field(default=None, metadata={"description": "Folder links to load documents from into embedded store on startup"})
    embedding_model_name : str = field(default="all-MiniLM-L6-v2", metadata={"description": "name of the embedding model to use for embedding store. Currently, only sentence transformer models are supported, e.g. all-MiniLM-L6-v2. See "})
    store_name : str = field(default=None, metadata={"description": "name of the embedded store"})
    
    def __post_init__(self):
        super().__post_init__()
        self._embedding_store = None
        self._embedding_model = None
        self._retriever = None
        self._non_text_extensions = {
            # Images (The most common cause of unwanted OCR/Tesseract triggers)
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".ico", ".svg",
            
            # Video & Audio
            ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm",
            ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg",
            
            # Executables, Binaries & System Files
            ".exe", ".dll", ".bin", ".dat", ".iso", ".sys", ".so", ".dylib", ".msi", ".bat",
            
            # Compressed & Archive Files
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
            
            # Design & Adobe Proprietary
            ".psd", ".ai", ".indd", ".eps", ".sketch", ".fig",
            
            # Font Files
            ".ttf", ".otf", ".woff", ".woff2"

            # Chroma db files
            ".db"

        }
            
    def _on_start(self):
        # attempt local download of embedding model
        if not os.path.exists(FileEmbeddingService.MODEL_RESOURCE_FOLDER / self.embedding_model_name):    
            model = SentenceTransformer(self.embedding_model_name)
            model.save(str(FileEmbeddingService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
            logger.debug("downloaded embedding model " + self.embedding_model_name + " to " + str(FileEmbeddingService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
        # Return tensors directly to avoid NumPy conversion issues and keep
        # compatibility with sentence-transformers versions that return lists
        # when only convert_to_numpy=False is set.
        self._embedding_model = HuggingFaceEmbeddings(
            model_name=os.path.join(str(FileEmbeddingService.MODEL_RESOURCE_FOLDER), self.embedding_model_name),
            encode_kwargs={"convert_to_tensor": True},
        )
        if self.store_name is None:
            self._embedding_store = Chroma(embedding_function=self._embedding_model)                       
        else:
            self._embedding_store = Chroma(persist_directory=os.path.join(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER, self.store_name), embedding_function=self._embedding_model)
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
    
    def add_document(self, document_link):
        # Check if document already in embedding store
        if self._embedding_store.get_by_ids([document_link + "_0"]): # check if document with id of document link + "_0" exists in embedding store, if yes, assume that all chunks of the document are already embedded and skip embedding for this document
            logger.debug("document " + document_link + " already embedded in embedding store, skipping embedding for this document")
            return
        # Only allow embedding of text-based documents, skip non-text files based on file extension to avoid unwanted OCR/Tesseract triggers and to save resources. This is a simple heuristic and can be further improved by actually checking the file type or content instead of just relying on the file extension, but it should work well in most cases and is much more efficient than trying to load every file and checking its content.
        if os.path.splitext(document_link)[1].lower() in self._non_text_extensions:
            logger.warning("skipping non-text file " + document_link + " for embedding")
            return
        loader = UnstructuredLoader(document_link, strategy="auto") 
        documents = loader.load()
        # filter for complex data        
        filtered_docs = filter_complex_metadata(documents) # Filter out documents with complex metadata that cannot be processed by the embedding model
        # Split into chunks
        # This is generally more "intelligent" than CharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        split_docs = text_splitter.split_documents(filtered_docs)
        self._embedding_store.add_documents(split_docs, ids=[document_link + "_" + str(i) for i in range(len(split_docs))]) # add document link as prefix to the id of the embedded document to ensure uniqueness and to be able to identify the source document of the embedded chunk later on when retrieving relevant documents from the embedding store
        logger.debug("embedded document " + document_link + " into embedding store")
    
