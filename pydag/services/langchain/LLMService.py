from dataclasses import dataclass, field
import enum

from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from loguru import logger

from ...services.ServiceException import ServiceException
from ...services.Service import Service

SYS_GENERAL_ASSISTANT : str = "You are a helpful assistant. Answer the following question:\n\n{question}"


class ModelProvider(str, enum.Enum):
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    # Add other providers as needed


@dataclass
class LLMService(Service):
    """`Service` for chat based LLM interaction
    """
    
    api_key : str = field(default=None, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description": "endpoint of the LLM provider"})
    model_provider : str = field(default=None, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | ..."})
    model : str = field(default=None, metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... "})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    system_message : str = field(default=SYS_GENERAL_ASSISTANT, metadata={"description":"Default System message to give to the LLM Agent"})
    
    def __post_init__(self):
        super().__post_init__()
        self.llm = None
        self.langchain = None
        self.session_histories = dict()  # to store chat history
       
    def __get_session_history(self, session_id: str):
        """Returns a persistent chat history for a given session."""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = InMemoryChatMessageHistory()
        return self.session_histories[session_id]
        
    def start(self):
        super().start()
        self._create_llm()                
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            chain  = prompt | self.llm # using pip operator to chain prompt and llm
            
            self.langchain = RunnableWithMessageHistory(
                chain,
                get_session_history=self.__get_session_history,
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )          
        else:
            prompt = PromptTemplate.from_template(
                self.system_message
            )
            self.langchain = prompt | self.llm
            
        logger.debug("created langchain with prompt template and llm")
    
    def stop(self):        
        self.langchain = None
        self.llm = None
        super().stop()
    
    def chat(self, question : str) -> str:
        if self.retain_messages:        
            ai_message = self.langchain.invoke({"question" : question}, config={"configurable" : {"session_id": "DEFAULT_SESSION"}})
        else:
            ai_message = self.langchain.invoke({"question" : question})
        #print(type(result))
        if isinstance(ai_message, str):
            return ai_message
        else:
            return ai_message.content
        
    def _create_llm(self):
        match self.model_provider:
            case ModelProvider.OPENAI.value:
                self.llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key, temperature=0)
            case ModelProvider.OLLAMA.value:
                self.llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        logger.debug("created LLM with model " + self.model + " from provider " + self.model_provider)