from dataclasses import dataclass, field
import enum

from langchain_core.messages import messages_from_dict
from langchain_core.messages.base import message_to_dict
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from loguru import logger

from ...services.ServiceException import ServiceException
from ...services.Service import Service
from ...agents.AgentElement import persisted_field, runtime_handle_field
from ...utils.ModelUtils import ModelUtils

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
    model_provider : str = field(default=ModelProvider.OPENAI.value, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended."})
    model : str = field(default="gpt-4.1-mini", metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default. "})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    system_message : str = field(default=SYS_GENERAL_ASSISTANT, metadata={"description":"Default System message to give to the LLM Agent"})
    _session_history_payloads : dict = persisted_field(default_factory=dict, init=False, repr=False)
    _llm : object = runtime_handle_field(default=None, init=False, repr=False)
    _langchain : RunnableWithMessageHistory | None = runtime_handle_field(default=None, init=False, repr=False)
    _session_histories : dict = runtime_handle_field(default_factory=dict, init=False, repr=False)
       
    def _get_session_history(self, session_id: str):
        """Returns a persistent chat history for a given session."""
        if session_id not in self._session_histories:
            self._session_histories[session_id] = InMemoryChatMessageHistory()
        return self._session_histories[session_id]
        
    def _on_start(self):
        self.rebuild_runtime_handles()

    def rebuild_runtime_handles(self, agent=None):
        self._restore_session_histories()
        if self._llm is not None and self._langchain is not None:
            return
        self._create_llm()
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            chain  = prompt | self._llm # using pip operator to chain prompt and llm
            
            self._langchain = RunnableWithMessageHistory(
                chain,
                get_session_history=self._get_session_history,
                input_messages_key="question",     # where to pull current user input
                history_messages_key="history"  # matches MessagesPlaceholder
            )          
        else:
            prompt = PromptTemplate.from_template(
                self.system_message
            )
            self._langchain = prompt | self._llm
            
        logger.debug("created langchain with prompt template and llm")

    def prepare_checkpoint(self, agent=None):
        super().prepare_checkpoint(agent)
        self._session_history_payloads = self._serialize_session_histories()
    
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
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        logger.debug("created LLM with model " + self.model + " from provider " + self.model_provider)

    def _serialize_session_histories(self) -> dict[str, list[dict]]:
        payload : dict[str, list[dict]] = {}
        for session_id, history in self._session_histories.items():
            payload[session_id] = [message_to_dict(message) for message in history.messages]
        return payload

    def _restore_session_histories(self):
        restored : dict[str, InMemoryChatMessageHistory] = {}
        for session_id, serialized_messages in self._session_history_payloads.items():
            history = InMemoryChatMessageHistory()
            history.messages = messages_from_dict(serialized_messages)
            restored[session_id] = history
        self._session_histories = restored
