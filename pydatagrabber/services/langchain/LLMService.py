from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory


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
        self.langchain = None
        self.session_histories = dict()  # to store chat history
    
    def install(self, grabber : Grabber = None):
        super().install()    
    
    def __get_session_history(self, session_id: str):
        """Returns a persistent chat history for a given session."""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = InMemoryChatMessageHistory()
        return self.session_histories[session_id]
        
    def start(self):
        match self.model_provider:
            case "OPENAI":
                llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key, temperature=0)
            case "OLLAMA":
                llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        self.LOGGER.debug("created LLM with model " + self.model + " from provider " + self.model_provider)
                
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            chain  = prompt | llm # using pip operator to chain prompt and llm
            
            self.langchain = RunnableWithMessageHistory(
                chain,
                get_session_history=self.__get_session_history,
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )
              
           
        else:
            prompt = PromptTemplate.from_template(
                "You are a helpful assistant. Answer the following question:\n\n{question}"
            )
            self.langchain = prompt | llm
            
        self.LOGGER.debug("created langchain with prompt template and llm")
    
    def stop(self):
        self.langchain = None
    
    def chat(self, question : str) -> str:
        if self.retain_messages:        
            ai_message = self.langchain.invoke({"question" : question}, config={"configurable" : {"session_id": "DEFAULT_SESSION"}})
        else:
            ai_message = self.langchain.invoke({"question" : question})
        #print(type(result))
        return ai_message.content