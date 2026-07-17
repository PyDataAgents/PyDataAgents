from dataclasses import dataclass, field
import enum
import os

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from loguru import logger

from ...services.ServiceException import ServiceException
from ...services.Service import Service
from ...utils.LLMUtils import build_message_history_input, compile_message_history_graph, get_message_content
from ...utils.ModelUtils import ModelUtils

SYS_GENERAL_ASSISTANT : str = "You are a helpful assistant. Answer the following question:\n\n{question}"
DEFAULT_INTERNET_SEARCH_MAX_RESULTS: int = 5
OllamaLLM = None


class ModelProvider(str, enum.Enum):
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    AZURE = "AZURE"
    LANGDOCK = "LANGDOCK"
    # Add other providers as needed


@dataclass
class LLMService(Service):
    """`Service` for chat based LLM interaction.

    Internet context uses Tavily and requires a Tavily API key configured as
    `tavily_api_key` or the `TAVILY_API_KEY` environment variable.
    """
    
    api_key : str = field(default=None, metadata={"description": "api token for a web based model provider, e.g. OPENAI"})
    endpoint : str = field(default=None, metadata={"description": "endpoint of the LLM provider"})
    model_provider : str = field(default=ModelProvider.OPENAI.value, metadata={"description": "name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended."})
    model : str = field(default="gpt-4.1-mini", metadata={"description": "name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default. "})
    retain_messages : bool = field(default=False, metadata={"description": "specify True if you want to retain the chat history for context"})
    system_message : str = field(default=SYS_GENERAL_ASSISTANT, metadata={"description":"Default System message to give to the LLM Agent"})
    use_internet_context: bool = field(default=False, metadata={"description": "Set to True to enrich prompts with Tavily internet search results before calling the model. Requires a Tavily API key."})
    tavily_api_key: str = field(default=None, metadata={"description": "Tavily API key for internet context. If omitted, TAVILY_API_KEY is read from the environment."})
    
    def __post_init__(self):
        super().__post_init__()
        self._llm = None
        self._langchain = None
        self._internet_search_tool = None
        
    def _on_start(self):
        self._create_llm()                
        if self.retain_messages:
            prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ])
            
            chain  = prompt | self._llm # using pip operator to chain prompt and llm

            def call_model(state, history_messages):
                return chain.invoke({
                    "history": history_messages,
                    "question": state["question"],
                })

            self._langchain = compile_message_history_graph(call_model)
        else:
            prompt = PromptTemplate.from_template(
                self.system_message
            )
            self._langchain = prompt | self._llm
            
        logger.debug("created langchain with prompt template and llm")
    
    def _on_stop(self):        
        self._langchain = None
        self._llm = None
        self._internet_search_tool = None
    
    def chat(self, question : str, use_internet_context: bool | None = None) -> str:
        internet_context = self._get_internet_context_text(question, use_internet_context=use_internet_context)
        model_question = question if internet_context == "" else (
            "Question:\n"
            + str(question)
            + "\n\nInternet Context:\n"
            + internet_context
            + "\n\nUse the internet context only when it is relevant to the question."
        )
        if self.retain_messages:        
            ai_message = self._langchain.invoke(
                build_message_history_input({"question": model_question}),
                config={"configurable" : {"thread_id": "DEFAULT_SESSION"}},
            )
        else:
            ai_message = self._langchain.invoke({"question" : model_question})
        return get_message_content(ai_message)

    def _get_internet_context_text(self, query: str | None, use_internet_context: bool | None = None) -> str:
        if use_internet_context is False or not self.use_internet_context:
            return ""
        if query is None or str(query).strip() == "":
            return ""

        if self._internet_search_tool is None:
            self._internet_search_tool = self._create_internet_search_tool()
        return self._format_internet_search_result(self._internet_search_tool.invoke(str(query)))

    def _create_internet_search_tool(self):
        try:
            from langchain_tavily import TavilySearch
        except ImportError as exc:
            raise ServiceException("Tavily internet context requires langchain_tavily.") from exc
        api_key = self.tavily_api_key or os.getenv("TAVILY_API_KEY")
        if api_key is None or str(api_key).strip() == "":
            raise ServiceException("Tavily internet context requires tavily_api_key or TAVILY_API_KEY.")
        return TavilySearch(max_results=DEFAULT_INTERNET_SEARCH_MAX_RESULTS, tavily_api_key=api_key)

    def _format_internet_search_result(self, result) -> str:
        if isinstance(result, dict) and isinstance(result.get("results"), list):
            return "\n".join(self._format_internet_search_item(idx, item) for idx, item in enumerate(result["results"], start=1))
        return "" if result is None else str(result).strip()

    def _format_internet_search_item(self, idx: int, item) -> str:
        if not isinstance(item, dict):
            return str(idx) + ". " + str(item).strip()
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        content = str(item.get("content", item.get("raw_content", item.get("answer", "")))).strip()
        return str(idx) + ". " + " | ".join(
            part for part in ["Title: " + title if title else "", "URL: " + url if url else "", "Content: " + content if content else ""] if part
        )

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
                global OllamaLLM
                if OllamaLLM is None:
                    from langchain_ollama import OllamaLLM as _OllamaLLM
                    OllamaLLM = _OllamaLLM
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
