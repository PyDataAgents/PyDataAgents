from dataclasses import dataclass, field
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.runnables import RunnableMap
import requests

from ...services.langchain.LLMService import LLMService
from ...services.ServiceException import ServiceException

@dataclass
class RAGService(LLMService):
    """Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form
    """
    
    # Constants
    MODEL_RESOURCE_FOLDER = Path("./resources/models/")
    
    document_links : list[str] = field(default_factory=list(), metadata={"description": "list of document links to load into embedded store on startup"})
    ignore_invalid_documents : bool = field(default=False, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    embedding_model_name : str = field(default="all-MiniLM-L6-v2", metadata={"description": "name of the embedding model to use for embedding store"})
    persist_directory : str = field(default=None, metadata={"description": "directory for persisting the embedded store"})
    
    def __init__(self):
        super().__init__()
        self.langchain = None
        self.embedding_store = None
        self.embedding_model = None
        self.retriever = None
        self.document_links = list()
            
    def start(self):
        # attempt local download of embedding model
        if not os.path.exists(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name):    
            model = SentenceTransformer(self.embedding_model_name)
            model.save(str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
            self.LOGGER.debug("downloaded embedding model " + self.embedding_model_name + " to " + str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
        self.embedding_model = HuggingFaceEmbeddings(model_name=str(RAGService.MODEL_RESOURCE_FOLDER / self.embedding_model_name))
        if self.persist_directory is None:
            self.embedding_store = Chroma(embedding_function=self.embedding_model)                       
        else:
            self.embedding_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_model)
        self.LOGGER.debug("created embedding store with embedding model " + self.embedding_model_name)
        for document_link in self.document_links:
            self.add_document(document_link)
            self.LOGGER.debug("emebedded cocument " + document_link + " into embedding store")
        self.retriever = self.embedding_store.as_retriever()
        match self.model_provider:
            case "OPENAI":
                llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key)
            case "OLLAMA":
                llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        self.LOGGER.debug("created LLM with model " + self.model + " from provider " + self.model_provider)
                
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Nutze den folgenden Kontext, um die Frage zu beantworten:\n{context}"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            #chain  = prompt | llm # using pipe operator to chain prompt and llm
            
            retrieval_chain = (
                {"question": lambda x: x["question"], "history": lambda x: x["history"]}
                | RunnableMap({
                    "context": lambda x: "\n\n".join([doc.page_content for doc in self.retriever.get_relevant_documents(x["question"])]),
                    "history": lambda x: x["history"],
                    "question": lambda x: x["question"],
                })
                | prompt
                | llm
            )
            
            self.langchain = RunnableWithMessageHistory(
                retrieval_chain,
                get_session_history=lambda session_id: InMemoryChatMessageHistory(),
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )
            
        else:
            prompt = PromptTemplate.from_template(
                "You are a helpful assistant. Answer the following question:\n\n{question}"
            )
            
            #self.langchain = prompt | llm # using pipe operator to chain prompt and llm
            self.langchain = (
                {"question": lambda x: x["question"]}
                | RunnableMap({
                    "context": lambda x: self.retriever.get_relevant_documents(x["question"]),
                    "question": lambda x: x["question"]
                })
                | prompt
                | llm
            )
            
        self.LOGGER.debug("created langchain with prompt template and llm")
    
    def stop(self):
        self.langchain = None
        self.embedding_store = None
        self.embedding_model = None
        self.retriever = None
    
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
    
    def chat(self, question : str) -> str:
        #self.LOGGER.debug(self.retriever.get_relevant_documents(question))
        if self.retain_messages:        
            ai_message = self.langchain.invoke({"question" : question}, config={"configurable" : {"session_id": "DEFAULT_SESSION"}})
        else:
            ai_message = self.langchain.invoke({"question" : question})
        #print(type(result))
        if isinstance(ai_message, str):
            return ai_message
        else:
            return ai_message.content
    
    @staticmethod
    def __load_pdf_from_url(url, local_path="temp.pdf"):
        r = requests.get(url, timeout=20)
        with open(local_path, "wb") as f:
            f.write(r.content)

        loader = UnstructuredLoader(local_path)
        documents = loader.load()
        os.remove(local_path)
        return documents
