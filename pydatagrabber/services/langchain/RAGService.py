from dataclasses import dataclass, field
import os

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain
from langchain_community.vectorstores.utils import filter_complex_metadata
import requests

from ...services.Service import Service
from ...services.ServiceException import ServiceException
from ...grabbers.Grabber import Grabber


@dataclass
class RAGService(Service):
    """Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form

    """
    
    api_key : str = field(default=None, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description": "endpoint of the LLM provider"})
    model_provider : str = field(default=None, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | ..."})
    model : str = field(default=None, metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... "})
    document_links : list[str] = field(default_factory=list(), metadata={"description": "list of document links to load into embedded store on startup"})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    ignore_invalid_documents : bool = field(default=False, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    embedding_model : str = field(default="all-MiniLM-L6-v2", metadata={"description": "name of the embedding model to use for embedding store"})
    persist_directory : str = field(default=None, metadata={"description": "directory for persisting the embedded store"})
    
    def __init__(self):
        super().__init__()
        self.embedding_store = None
        self.retriever = None
        self.retrieval_chain = None
        self.document_links = list()
    
    def install(self, grabber : Grabber = None):
        super().install()
        
    def start(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.embedding_model)
        if self.persist_directory is None:
            self.embedding_store = Chroma(embedding_function=self.embedding_model)
            for document_link in self.document_links:
                self.add_document(document_link)
        else:
            self.embedding_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_model)
        self.retriever = self.embedding_store.as_retriever()
        match self.model_provider:
            case "OPENAI":
                llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key)
            case "OLLAMA":
                llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
                
        if self.retain_messages:
            self.retrieval_chain = LLMChain(
                llm = llm,
                retriever = self.retriever,
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                return_source_documents = True
            )
        else:
            self.retrieval_chain = LLMChain(
                llm = llm,
                retriever = self.retriever,
                return_source_documents = True
            )
    
    def stop(self):
        self.retrieval_chain = None
        self.embedding_store = None
        self.embedding_model = None
    
    def add_document(self, document_link):
        if "http" in  document_link and ".pdf" in document_link:
            documents = RAGService.__load_pdf_from_url(document_link) 
        else:
            loader = UnstructuredLoader(document_link)
            documents = loader.load()
        # filter for complex data        
        filtered_docs = filter_complex_metadata(documents)
        # Split into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_docs = text_splitter.split_documents(filtered_docs)
        self.embedding_store.add_documents(split_docs)

    def chat(self, question : str) -> dict:
        result = self.retrieval_chain.invoke(question)
        return result
    
    @staticmethod
    def __load_pdf_from_url(url, local_path="temp.pdf"):
        r = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(r.content)

        loader = UnstructuredLoader(local_path)
        documents = loader.load()
        os.remove(local_path)
        return documents
