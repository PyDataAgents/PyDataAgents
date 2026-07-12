from dataclasses import dataclass, field
import enum

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from loguru import logger

from ...services.ServiceException import ServiceException
from ...services.Service import Service
from ...utils.ModelUtils import ModelUtils

SYS_GENERAL_ASSISTANT : str = "You are a helpful assistant. Answer the following question:\n\n{question}"


class ModelProvider(str, enum.Enum):
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    AZURE = "AZURE"
    LANGDOCK = "LANGDOCK"
    # Add other providers as needed


@dataclass
class LLMService(Service):
    """`Service` for chat based LLM interaction
    """
    
    api_key : str = field(default=None, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description": "endpoint of the LLM provider"})
    model_provider : str = field(default=ModelProvider.OPENAI.value, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended."})
    model : str = field(default="gpt-4.1-mini", metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default. "})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    system_message : str = field(default=SYS_GENERAL_ASSISTANT, metadata={"description":"Default System message to give to the LLM Agent"})
    
    def __post_init__(self):
        super().__post_init__()
        self._llm = None
        self._langchain : RunnableWithMessageHistory = None
        self._session_histories = dict()  # to store chat history
       
    def __get_session_history(self, session_id: str):
        """Returns a persistent chat history for a given session."""
        if session_id not in self._session_histories:
            self._session_histories[session_id] = InMemoryChatMessageHistory()
        return self._session_histories[session_id]
        
    def _on_start(self):
        self._create_llm()                
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            chain  = prompt | self._llm # using pip operator to chain prompt and llm
            
            self._langchain = RunnableWithMessageHistory(
                chain,
                get_session_history=self.__get_session_history,
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )          
        else:
            prompt = PromptTemplate.from_template(
                self.system_message
            )
            self._langchain = prompt | self._llm
            
        logger.debug("created langchain with prompt template and llm")
    
    def _on_stop(self):        
        self._langchain = None
        self._llm = None
    
    def chat(self, question : str) -> str:
        if self.retain_messages:        
            ai_message = self._langchain.invoke({"question" : question}, config={"configurable" : {"session_id": "DEFAULT_SESSION"}})
        else:
            ai_message = self._langchain.invoke({"question" : question})
        #print(type(result))
        if isinstance(ai_message, str):
            return ai_message
        else:
            return ai_message.content
        
    def _create_llm(self):
        match self.model_provider:
            case ModelProvider.OPENAI.value:
                self._llm = ChatOpenAI(model_name=self.model, openai_api_key=self.api_key, temperature=1)
            
            case ModelProvider.AZURE.value:
                self._llm = AzureChatOpenAI(
                    azure_deployment=self.model,
                    api_version="2024-02-15-preview",
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    temperature=0
                )
            
            case ModelProvider.OLLAMA.value:
                try:
                    ModelUtils.ensure_ollama_model_available(self.model, self.endpoint)
                except Exception as exc:
                    endpoint_display = self.endpoint if self.endpoint is not None and str(self.endpoint).strip() != "" else "http://localhost:11434"
                    raise ServiceException(
                        "Failed to ensure Ollama model '"
                        + str(self.model)
                        + "' at endpoint '"
                        + str(endpoint_display)
                        + "' for "
                        + self.cname()
                        + ". "
                        + str(exc)
                    ) from exc
                self._llm = OllamaLLM(model = self.model, base_url = self.endpoint)
            
            case ModelProvider.LANGDOCK.value:
                if self.endpoint is None or str(self.endpoint).strip() == "":
                    raise ServiceException("Langdock endpoint must be configured for " + self.__class__.__name__)

                self._llm = ChatOpenAI(
                    model_name=self.model,
                    openai_api_key=self.api_key,
                    base_url=self.endpoint,
                    temperature=1,
                )
            
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        logger.debug("created LLM with model " + self.model + " from provider " + self.model_provider)
