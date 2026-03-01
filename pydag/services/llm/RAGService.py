from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from loguru import logger
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.runnables import RunnableMap
from pydag.agents.AgentConfig import AgentConfig

from ..llm.LLMService import LLMService
from ...services.ServiceException import ServiceException


@dataclass
class RAGService(LLMService):
    """Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form."""

    # Constants
    MODEL_RESOURCE_FOLDER = Path(AgentConfig.MODEL_RESOURCE_FOLDER)
    CHROMA_DB_FILENAMES = {"chroma.db", "chroma.sqlite3"}

    document_links: list[str] = field(default_factory=list, metadata={"description": "list of document links to load into embedded store on startup"})
    ignore_invalid_documents: bool = field(default=False, metadata={"description": "deprecated compatibility field (no-op)"})
    embedding_model_name: str = field(default="all-MiniLM-L6-v2", metadata={"description": "name of the embedding model to use for embedding store"})
    persist_directory: str = field(default=None, metadata={"description": "directory for persisting the embedded store"})
    vector_store_path: str = field(default=None, metadata={"description": "path to existing chroma.db/chroma.sqlite3 file or its directory. Use this, if a pre-existing vector store should be used. If both vector_store_path and persist_directory are provided, vector_store_path takes precedence."})

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
            ".ttf", ".otf", ".woff", ".woff2",

            # Chroma db files
            ".db", ".sqlite", ".sqlite3"
        }

    def _on_start(self):
        # attempt local download of embedding model
        if not os.path.exists(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name):
            model = SentenceTransformer(self.embedding_model_name)
            model.save(str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
            logger.debug("downloaded embedding model " + self.embedding_model_name + " to " + str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
        # Return tensors directly to avoid NumPy conversion issues and keep
        # compatibility with sentence-transformers versions that return lists
        # when only convert_to_numpy=False is set.
        self._embedding_model = HuggingFaceEmbeddings(
            model_name=str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name),
            encode_kwargs={"convert_to_tensor": True},
        )

        resolved_directory = self._resolve_vector_store_directory()
        if resolved_directory is None:
            self._embedding_store = Chroma(embedding_function=self._embedding_model)
        else:
            self._embedding_store = Chroma(persist_directory=resolved_directory, embedding_function=self._embedding_model)
        logger.debug("created embedding store with embedding model " + self.embedding_model_name)

        if len(self.document_links) > 0:
            self.add_documents(self.document_links)

        self._retriever = self._embedding_store.as_retriever()
        self._create_llm_and_chain()

    def _create_llm_and_chain(self):
        self._create_llm()

        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_message),
                MessagesPlaceholder(variable_name="history"),
                ("human", "Question:\n{question}\n\nInstruction:\n{instruction}\n\nLocal Input Context:\n{input_context}\n\nRetrieved Context:\n{context}"),
            ])

            retrieval_chain = (
                {
                    "question": lambda x: x["question"],
                    "instruction": lambda x: x.get("instruction", ""),
                    "input_context": lambda x: x.get("input_context", ""),
                    "retrieval_query": lambda x: x.get("retrieval_query", x["question"]),
                    "use_rag_context": lambda x: x.get("use_rag_context", True),
                    "history": lambda x: x["history"],
                }
                | RunnableMap({
                    "context": lambda x: self._get_retrieved_context_text(
                        retrieval_query=x["retrieval_query"],
                        use_rag_context=x["use_rag_context"],
                    ),
                    "history": lambda x: x["history"],
                    "question": lambda x: x["question"],
                    "instruction": lambda x: x["instruction"],
                    "input_context": lambda x: x["input_context"],
                })
                | prompt
                | self._llm
            )

            self._langchain = RunnableWithMessageHistory(
                retrieval_chain,
                get_session_history=self._get_session_history,
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )

        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_message),
                ("human", "Question:\n{question}\n\nInstruction:\n{instruction}\n\nLocal Input Context:\n{input_context}\n\nRetrieved Context:\n{context}"),
            ])

            self._langchain = (
                {
                    "question": lambda x: x["question"],
                    "instruction": lambda x: x.get("instruction", ""),
                    "input_context": lambda x: x.get("input_context", ""),
                    "retrieval_query": lambda x: x.get("retrieval_query", x["question"]),
                    "use_rag_context": lambda x: x.get("use_rag_context", True),
                }
                | RunnableMap({
                    "context": lambda x: self._get_retrieved_context_text(
                        retrieval_query=x["retrieval_query"],
                        use_rag_context=x["use_rag_context"],
                    ),
                    "question": lambda x: x["question"],
                    "instruction": lambda x: x["instruction"],
                    "input_context": lambda x: x["input_context"],
                })
                | prompt
                | self._llm
            )

        logger.debug("created langchain with prompt template and llm")

    def _on_stop(self):
        self._langchain = None
        self._embedding_store = None
        self._embedding_model = None
        self._retriever = None
        self._session_histories = {}

    def _get_session_history(self, session_id: str):
        """Returns a persistent chat history for a given session."""
        if session_id not in self._session_histories:
            self._session_histories[session_id] = InMemoryChatMessageHistory()
        return self._session_histories[session_id]

    def _serialize_input_context(self, input_context: str | dict | list | None) -> str:
        if input_context is None:
            return ""
        if isinstance(input_context, str):
            return input_context
        try:
            return json.dumps(input_context, ensure_ascii=True)
        except Exception:
            return str(input_context)

    def _get_retrieved_context_text(self, retrieval_query: str, use_rag_context: bool = True) -> str:
        if not use_rag_context:
            return ""
        if retrieval_query is None or str(retrieval_query).strip() == "":
            return ""
        docs = self._retriever.get_relevant_documents(str(retrieval_query))
        return "\n\n".join([getattr(doc, "page_content", str(doc)) for doc in docs])

    def _resolve_vector_store_directory(self):
        configured_path = self.vector_store_path
        if configured_path and self.persist_directory:
            logger.warning("Both vector_store_path and persist_directory are configured. vector_store_path takes precedence.")
        if configured_path is None:
            configured_path = self.persist_directory
        if configured_path is None:
            return None

        configured_path = os.path.normpath(configured_path)
        basename = os.path.basename(configured_path).lower()
        extension = os.path.splitext(configured_path)[1].lower()

        # explicit chroma db file path
        if basename in RAGService.CHROMA_DB_FILENAMES or extension in {".db", ".sqlite", ".sqlite3"}:
            parent = os.path.dirname(configured_path)
            return parent if parent != "" else "."

        if os.path.isdir(configured_path):
            return configured_path

        # Non-existing path -> treat as target directory path
        return configured_path

    def _is_document_link_url(self, document_link: str) -> bool:
        parsed = urlparse(document_link)
        return parsed.scheme in {"http", "https"} and parsed.netloc != ""

    def _is_non_text_document(self, document_link: str) -> bool:
        if self._is_document_link_url(document_link):
            path = urlparse(document_link).path
            extension = os.path.splitext(path)[1].lower()
        else:
            extension = os.path.splitext(document_link)[1].lower()
        return extension in self._non_text_extensions

    def add_documents(self, document_links: list[str] | str):
        if isinstance(document_links, str):
            document_links = [document_links]

        if document_links is None or len(document_links) == 0:
            return

        for _document_link in document_links:
            if self._is_document_link_url(_document_link):
                self.add_document(_document_link)
                continue

            _document_link = os.path.join(_document_link)
            if os.path.isdir(_document_link):
                for root, _, files in os.walk(_document_link):
                    for _doc in files:
                        document_link = root + os.sep + _doc
                        self.add_document(document_link)
            elif os.path.isfile(_document_link):
                self.add_document(_document_link)
            else:
                raise ServiceException("The link " + str(_document_link) + " is not a valid document file, folder or URL.")

    def add_document(self, document_link):
        # Check if document already in embedding store
        if self._embedding_store.get_by_ids([document_link + "_0"]):  # check if document with id of document link + "_0" exists in embedding store, if yes, assume that all chunks of the document are already embedded and skip embedding for this document
            logger.debug("document " + document_link + " already embedded in embedding store, skipping embedding for this document")
            return
        # Only allow embedding of text-based documents, skip non-text files based on file extension to avoid unwanted OCR/Tesseract triggers and to save resources. This is a simple heuristic and can be further improved by actually checking the file type or content instead of just relying on the file extension, but it should work well in most cases and is much more efficient than trying to load every file and checking its content.
        if self._is_non_text_document(document_link):
            logger.warning("skipping non-text file " + document_link + " for embedding")
            return
        loader = UnstructuredLoader(document_link, strategy="auto")
        documents = loader.load()
        # filter for complex data
        filtered_docs = filter_complex_metadata(documents)  # Filter out documents with complex metadata that cannot be processed by the embedding model
        # Split into chunks
        # This is generally more "intelligent" than CharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        split_docs = text_splitter.split_documents(filtered_docs)
        self._embedding_store.add_documents(split_docs, ids=[document_link + "_" + str(i) for i in range(len(split_docs))])  # add document link as prefix to the id of the embedded document to ensure uniqueness and to be able to identify the source document of the embedded chunk later on when retrieving relevant documents from the embedding store
        logger.debug("embedded document " + document_link + " into embedding store")
        if document_link not in self.document_links:
            self.document_links.append(document_link)

    def chat(
        self,
        question: str,
        instruction: str | None = None,
        input_context: str | dict | list | None = None,
        retrieval_query: str | None = None,
        use_rag_context: bool = True,
        session_id: str = "DEFAULT_SESSION",
    ) -> str:
        """Chat with RAG-backed context.

        Args:
            question: The final task/question the model must answer. This is what the generated answer should respond to.
            instruction: Rules on how to answer (format, style, constraints, priorities).
            input_context: Additional runtime context passed directly from parent buffers (not retrieved from vector DB).
            retrieval_query: The query used only for document retrieval from the vector store.
            use_rag_context: Set to False to disable retrieval and answer only from the prompt payload.
            session_id: Session id used for retained message history.
        """
        if question is None or str(question).strip() == "":
            raise ServiceException("question must not be empty for " + self.cname())

        payload = {
            "question": str(question),
            "instruction": "" if instruction is None else str(instruction),
            "input_context": self._serialize_input_context(input_context),
            "retrieval_query": str(question) if retrieval_query is None else str(retrieval_query),
            "use_rag_context": bool(use_rag_context),
        }

        if self.retain_messages:
            ai_message = self._langchain.invoke(
                payload,
                config={"configurable": {"session_id": session_id}},
            )
        else:
            ai_message = self._langchain.invoke(payload)
        if isinstance(ai_message, str):
            return ai_message
        else:
            return ai_message.content
