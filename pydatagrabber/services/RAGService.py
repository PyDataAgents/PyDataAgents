from dataclasses import dataclass, field

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

from ..grabbers.Grabber import Grabber
from .Service import Service


@dataclass
class RAGService(Service):
    """Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form

    """
    
    api_key : str = field(default=None, metadata={"description", "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description", "endpoint of the LLM provider"})
    model_provider : str = field(default=None, metadata={"description", "name of the model provider, e.g. OPENAI | OLLAMA | ..."})
    model : str = field(default=None, metadata={"description", "name of the model, e.g. gpt-4o | gemma:1b | ... "})
    document_links : list[str] = field(default=None, metadata={"description", "list of document links to load into embedded store on startup"})
    retained_messages : int = field(default=10, metadata={"description", "messages to retain in chat for context"})
    ignore_invalid_documents : bool = field(default=False, metadata={"description", "api token for a web based model provider, e.g. OPENAI"})
    embedding_model : str = field(default="all-MiniLM-L6-v2", metadata={"description", "name of the embedding model to use for embedding store"})
    persist_directory : str = field(default=None, metadata={"description", "directory for persisting the embedded store"})
    
    def __init__(self):
        super().__init__()
        self.embedding_store = None
        self.retriever = None
        self.qa_chain = None
    
    def install(self, grabber : Grabber = None):
        super().install()
        
    def start(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.embedding_model)
        if self.persist_directory is None:
            self.embedding_store = Chroma(embedding_function=self.embedding_model)
        else:
            self.embedding_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_model)
        for document_link in self.document_links:
            self.add_document(document_link)
        self.retriever = self.embedding_store.as_retriever(search_kwargs={"k": self.retained_messages})
        match self.model_provider:
            case "OPENAI":
                llm = OpenAI(model_name=self.model)
            case "OLLAMA":
                pass
    
        self.qa_chain = RetrievalQA.from_chain_type(
            llm = llm,
            retriever = self.retriever,
            return_source_documents = True
        )
    
    def stop(self):
        pass
    
    def add_document(self, document_link):
        if "http://" in document_link or "https://" in document_link:
            loader = UnstructuredURLLoader(urls=document_link)
        else:
            loader = UnstructuredFileLoader(document_link)
        documents = loader.load()
        # Split into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_docs = text_splitter.split_documents(documents)
        self.embedding_store.add_documents(split_docs)
        if self.persist_directory is not None:
            self.embedding_store.persist()

    def chat(self, question : str) -> str:
        result = self.qa_chain(question)
        return result
