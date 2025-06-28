from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain

from ...services.ServiceException import ServiceException
from ...grabbers.Grabber import Grabber
from ...services.Service import Service


@dataclass
class LLMService(Service):
    """LLM Service for chat based LLM interaction

    """
    
    api_key : str = field(default=None, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description": "endpoint of the LLM provider"})
    model_provider : str = field(default=None, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | ..."})
    model : str = field(default=None, metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... "})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    
    def __init__(self):
        super().__init__()
        self.embedding_store = None
        self.retriever = None
        self.retrieval_chain = None
    
    def install(self, grabber : Grabber = None):
        super().install()
        
    def start(self):
        match self.model_provider:
            case "OPENAI":
                llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key)
            case "OLLAMA":
                llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
                
        if self.retain_messages:
            self.retrieval_chain = LLMChain(
                llm=llm,
                memory=ConversationBufferMemory()
            )
        else:
            self.retrieval_chain = LLMChain(
                llm=llm
            )
    
    def stop(self):
        self.retrieval_chain = None
    
    def chat(self, question : str) -> dict:
        result = self.retrieval_chain.run(question)
        return result