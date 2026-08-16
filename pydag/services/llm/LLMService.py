import base64
from dataclasses import dataclass, field
import enum
import mimetypes
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
import warnings

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from loguru import logger

from ...services.ServiceException import ServiceException
from ...services.Service import Service
from ...utils.LLMUtils import build_message_history_input, compile_message_history_graph, get_message_content

SYS_GENERAL_ASSISTANT : str = "You are a helpful assistant. Answer the following question:\n\n{question}"
DEFAULT_INTERNET_SEARCH_MAX_RESULTS: int = 5
GENERIC_FILE_MIME_TYPE: str = "application/octet-stream"


class ModelProvider(str, enum.Enum):
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    AZURE = "AZURE"
    LANGDOCK = "LANGDOCK"
    MISTRAL = "MISTRAL"
    # Add other providers as needed


@dataclass
class ContextFile:
    source: str
    value: str | bytes
    filename: str
    mime_type: str


@dataclass
class LLMService(Service):
    """`Service` for chat based LLM interaction.

    Internet context uses Tavily and requires a Tavily API key configured as
    `tavily_api_key` or the `TAVILY_API_KEY` environment variable.

    File inputs use `context_files` and may be URLs, file URLs, local paths
    (absolute or relative to the current working directory), data URIs, base64
    strings, bytes, or lists. OPENAI and AZURE send them to the model; OLLAMA
    warns and continues text-only.
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
                if self._context_files_supplied(state.get("context_files")):
                    return self._invoke_model_with_context_files(
                        prompt_text=state["question"],
                        context_files=state["context_files"],
                        history_messages=history_messages,
                    )
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
    
    def chat(
        self,
        question: str,
        use_internet_context: bool | None = None,
        context_files: str | bytes | list[str | bytes] | None = None,
    ) -> str:
        """Chat with optional file context for OPENAI/AZURE; OLLAMA warns and ignores files."""
        internet_context = self._get_internet_context_text(question, use_internet_context=use_internet_context)
        model_question = question if internet_context == "" else (
            "Question:\n"
            + str(question)
            + "\n\nInternet Context:\n"
            + internet_context
            + "\n\nUse the internet context only when it is relevant to the question."
        )
        context_files = self._prepare_context_files_for_provider(context_files)

        if self.retain_messages:        
            ai_message = self._langchain.invoke(
                build_message_history_input({"question": model_question, "context_files": context_files}),
                config={"configurable" : {"thread_id": "DEFAULT_SESSION"}},
            )
        else:
            if self._context_files_supplied(context_files):
                ai_message = self._invoke_model_with_context_files(
                    prompt_text=self._format_service_prompt_text(model_question),
                    context_files=context_files,
                )
            else:
                ai_message = self._langchain.invoke({"question" : model_question})
        return get_message_content(ai_message)

    def _format_service_prompt_text(self, question: str) -> str:
        try:
            return self.system_message.format(question=question)
        except Exception:
            return str(self.system_message) + "\n\n" + str(question)

    def _prepare_context_files_for_provider(self, context_files):
        if not self._context_files_supplied(context_files):
            return None
        if self.model_provider == ModelProvider.OLLAMA.value:
            self._handle_ollama_context_files_placeholder(context_files)
            return None
        return context_files

    def _handle_ollama_context_files_placeholder(self, context_files) -> None:
        _ = context_files
        message = "File inputs are currently supported only for OPENAI and AZURE models. OLLAMA file processing is not implemented yet; supplied files will be ignored."
        logger.warning(message)
        warnings.warn(message, RuntimeWarning, stacklevel=2)

    def _context_files_supplied(self, context_files) -> bool:
        return context_files is not None and context_files != []

    def _invoke_model_with_context_files(
        self,
        prompt_text: str,
        context_files,
        history_messages: list | None = None,
        system_message: str | None = None,
    ):
        if self.model_provider not in {ModelProvider.OPENAI.value, ModelProvider.AZURE.value}:
            raise ServiceException(
                "File inputs are supported only for OPENAI and AZURE providers in " + self.cname()
            )

        content_blocks = [{"type": "text", "text": str(prompt_text)}] + [
            self._context_file_to_content_block(file) for file in self._normalize_context_files(context_files)
        ]
        messages = (
            ([SystemMessage(content=str(system_message))] if system_message is not None and str(system_message).strip() != "" else [])
            + (history_messages or [])
            + [HumanMessage(content=content_blocks)]
        )

        if hasattr(self._llm, "invoke"):
            return self._llm.invoke(messages)
        return self._llm(messages)

    def _normalize_context_files(self, context_files) -> list[ContextFile]:
        if context_files is None:
            return []
        items = context_files if isinstance(context_files, list) else [context_files]
        return [self._normalize_context_file(item, idx) for idx, item in enumerate(items, start=1)]

    def _normalize_context_file(self, item, idx: int) -> ContextFile:
        default_filename = "context_file_" + str(idx)
        if isinstance(item, dict):
            raise ServiceException("context_files does not support dict descriptors")
        if isinstance(item, (bytes, bytearray)):
            return ContextFile(
                source="inline",
                value=bytes(item),
                filename=default_filename,
                mime_type=GENERIC_FILE_MIME_TYPE,
            )
        if not isinstance(item, str):
            raise ServiceException("context_files items must be str or bytes")

        text = item.strip()
        if text == "":
            raise ServiceException("context_files entries must not be empty")
        if text.startswith("data:"):
            if "," not in text:
                raise ServiceException("malformed context file data URI")
            header, encoded = text.split(",", 1)
            if ";base64" not in header:
                raise ServiceException("context file data URIs must use base64 encoding")
            mime_type = header.removeprefix("data:").split(";", 1)[0] or GENERIC_FILE_MIME_TYPE
            return ContextFile("inline", self._decode_base64_context_file(encoded), default_filename, mime_type)
        if self._is_absolute_local_path(text):
            return self._normalize_local_context_file(text)

        parsed = urlparse(text)
        if parsed.scheme in {"http", "https"}:
            if parsed.netloc == "":
                raise ServiceException("malformed context file URL: " + text)
            filename = os.path.basename(unquote(parsed.path)) or default_filename
            return ContextFile("remote", text, filename, self._guess_mime_type(filename))
        if parsed.scheme == "file":
            return self._normalize_local_context_file(self._path_from_file_url(text))
        if parsed.scheme != "":
            raise ServiceException("unsupported context file URL scheme: " + parsed.scheme)
        if os.path.exists(os.path.normpath(text)) or self._looks_like_relative_path(text):
            return self._normalize_local_context_file(text)

        return ContextFile("inline", self._decode_base64_context_file(text), default_filename, GENERIC_FILE_MIME_TYPE)

    def _normalize_local_context_file(self, file_path: str) -> ContextFile:
        normalized_path = os.path.normpath(file_path)
        if not os.path.isfile(normalized_path):
            raise ServiceException("context file does not exist: " + normalized_path)
        filename = os.path.basename(normalized_path) or "context_file"
        return ContextFile("local", normalized_path, filename, self._guess_mime_type(filename))

    def _path_from_file_url(self, file_url: str) -> str:
        parsed = urlparse(file_url)
        if parsed.scheme != "file":
            raise ServiceException("not a file URL: " + file_url)
        path = unquote(parsed.path)
        if parsed.netloc:
            path = "//" + parsed.netloc + path
        if re.match(r"^/[A-Za-z]:/", path):
            path = path[1:]
        return path

    def _is_absolute_local_path(self, value: str) -> bool:
        return os.path.isabs(value) or re.match(r"^[A-Za-z]:[\\/]", value) is not None

    def _looks_like_relative_path(self, value: str) -> bool:
        return value.startswith((".", "~")) or "\\" in value or ("/" in value and "." in value.rsplit("/", 1)[-1]) or ("/" not in value and "." in value)

    def _decode_base64_context_file(self, value: str) -> bytes:
        compact = "".join(str(value).split())
        if compact == "":
            raise ServiceException("context file base64 payload must not be empty")
        padding = "=" * (-len(compact) % 4)
        try:
            return base64.b64decode(compact + padding, validate=True)
        except Exception as exc:
            raise ServiceException("invalid context file base64 payload") from exc

    def _guess_mime_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or GENERIC_FILE_MIME_TYPE

    def _context_file_to_content_block(self, file: ContextFile) -> dict:
        if file.mime_type.startswith("image/"):
            if file.source == "remote":
                return {"type": "image_url", "image_url": {"url": str(file.value)}}
            if file.source in {"local", "inline"}:
                data = Path(str(file.value)).read_bytes() if file.source == "local" else bytes(file.value)
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:" + file.mime_type + ";base64," + base64.b64encode(data).decode("utf-8"),
                    },
                }
            raise ServiceException("unknown context file source type: " + str(file.source))

        block_type = "audio" if file.mime_type.startswith("audio/") else "file"
        if file.source == "remote":
            block = {"type": block_type, "url": str(file.value)}
        elif file.source in {"local", "inline"}:
            data = Path(str(file.value)).read_bytes() if file.source == "local" else bytes(file.value)
            block = {
                "type": block_type,
                "base64": base64.b64encode(data).decode("utf-8"),
                "mime_type": file.mime_type,
            }
        else:
            raise ServiceException("unknown context file source type: " + str(file.source))
        if block_type == "file":
            block.update({"filename": file.filename, "mime_type": file.mime_type})
        return block

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
                self._llm = ChatOllama(model = self.model, base_url = self.endpoint)
            
            case ModelProvider.LANGDOCK.value:
                if self.endpoint is None or str(self.endpoint).strip() == "":
                    raise ServiceException("Langdock endpoint must be configured for " + self.__class__.__name__)

                self._llm = ChatOpenAI(
                    model_name=self.model,
                    openai_api_key=self.api_key,
                    base_url=self.endpoint,
                    temperature=1,
                )
                
            case ModelProvider.MISTRAL.value:
                self._llm = ChatMistralAI(model=self.model, mistral_api_key=self.api_key, temperature=0)
            
            case _:
                raise ServiceException("Unknown Model " + self.model + " for " + self.cname())
        logger.debug("created LLM with model " + self.model + " from provider " + self.model_provider)
