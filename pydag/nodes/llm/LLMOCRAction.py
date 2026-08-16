from dataclasses import dataclass, field
import os
from loguru import logger
from mistralai import Mistral
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from ..NodeException import NodeException
from ...services.llm.LLMService import ModelProvider
from ...utils.StringUtils import StringUtils
from ...utils.DataUtils import DataUtils
from ...nodes.BufferNode import BufferNode
from ...nodes.Action import Action
from ...agents.Agent import Agent


@dataclass
class LLMOCRAction(BufferNode, Action):
    """ `Action` to retrieve text from an image or PDF and store the extracted text in its `Buffer`.
    The parent Buffer Node is expected to provide file paths to images or PDFs.
    The allowed input formats for the file paths are:
    - A fully qualified file path as a string
    - an image/pdf as a Base64-encoded data URL 
    
    depending on the model providers, the functionality is implemented in different ways:
    
    - Mistral:
        The Mistral OCR-3 model is used to extract text from the images or PDFs.
        For more information about the Mistral OCR-3 model: https://mistral.ai/news/mistral-ocr-3".

        The output has the following format:
        {
            "documents": <String of extracted text pages creatred from the contents of the origial OCRPageObject returned by Mistral>,
            "filepath": <file path for each processed input>
        }
        Where the original OCRPageObject has the following format:
            {
            "pages": [ # The content of each page
                {
                "index": int, # The index of the corresponding page
                "markdown": str, # The main output and raw markdown content
                "images": list, # Image information when images are extracted
                "tables": list, # Table information when using `table_format=html`
                "hyperlinks": list, # Hyperlinks detected
                "header": str|null, # Header content when using `extract_header=True`
                "footer": str|null, # Footer content when using `extract_footer=True`
                "dimensions": dict # The dimensions of the page
                }
            ],
            "model": str, # The model used for the OCR
            "document_annotation": dict|null, # Document annotation information when used, visit the Annotations documentation for more information
            "usage_info": dict # Usage information
            }
        See https://docs.mistral.ai/capabilities/document_ai/basic_ocr for more details.

    - Ollama:
        Uses the chat api of the Ollama Client
    
    - OpenAI:

    """

    api_key : str = field(default=None, metadata={"description": "a mistral ai api key"})
    output_keys : list[str] = field(default_factory=lambda: ["content", "filepath"])
    model_provider : str = field(default=ModelProvider.MISTRAL.value, metadata={"description": f"selection of model providers: {' | '.join([mp.value for mp in ModelProvider])}"})
    model : str = field(default="mistral-ocr-latest", metadata={"description": "Mistral OCR model name"})
    include_image_base64 : bool = field(default=False, metadata={"description": "Whether OCR page payloads should include embedded base64 images"})
    endpoint : str = field(default=None, metadata={"description": "endpoint for the model provider, if it has to be specified, e.g. OLLAMA"})
    
    def __post_init__(self):
        super().__post_init__()
        self._client = None

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        match self.model_provider:
            case ModelProvider.MISTRAL.value:
                self._client = Mistral(api_key=self.api_key)
            case ModelProvider.OLLAMA.value:
                self._client = ChatOllama(model = self.model, base_url = self.endpoint)
            case _:
                raise NodeException(f"Could not install {self.__class__.__name__}, because of unknown {ModelProvider.__name__} {self.model_provider}")

    def _on_execute(self):    
        data = self.get_parent_data(by_rows=True)
        row : dict
        for row in data:
            for val in row.values():
                file_ref = str(val)
                if file_ref == "":
                    continue
                document_payload, file_path = self._resolve_document_payload(file_ref)
                if document_payload is None:
                    continue
                match self.model_provider:
                    case ModelProvider.MISTRAL.value:    
                        resp = self._client.ocr.process(
                            model=self.model,
                            document=document_payload,
                            include_image_base64=self.include_image_base64,
                        )
                        answer = self._serialize_ocr_response(resp)
                    case ModelProvider.OLLAMA.value:
                        message : HumanMessage = HumanMessage(
                            content=[
                                {
                                    "type": "text",
                                    "text": "Extract all text from the given document. Do not summarize and only return text."                                        
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": document_payload
                                    }
                                }
                            ]
                        )
                        response = self._client.invoke([message])
                        answer = response.content
                    case ModelProvider.OPENAI.value:
                        pass                
                    case _:
                        raise NodeException(f"Unknown ModelProvider {self.model_provider} was specified")
                    
                dic = dict(zip(self.output_keys, [answer, file_path]))
                self.add_data(dic)

    def _resolve_document_payload(self, file_ref: str):
        file_path = None
        file_type = file_ref.split(".")[-1].lower()
        if os.path.isfile(file_ref):
            file_path = file_ref
            file_ref = DataUtils.file_to_base64(file_ref)
            if file_ref is None:
                return None, None
        elif "data:image/" in file_ref:
            file_type = file_ref.split("data:image/")[1].split(";base64")[0]
        elif file_ref.startswith("data:application/pdf"):
            file_type = "pdf"
        elif StringUtils.is_valid_url(file_ref):
            file_path = file_ref
        else:
            logger.debug(f"could not detect supported OCR input: {file_ref}")
            return None, None

        if file_type in ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]:
            return {
                "type": "image_url",
                "image_url": file_ref,
            }, file_path
        elif file_type == "pdf":
            return {
                "type": "document_url",
                "document_url": file_ref,
            }, file_path
        else:
            return None, None

    def _serialize_ocr_response(self, response) -> str:
        pages = getattr(response, "pages", []) or []
        parts: list[str] = []
        for page in pages:
            page_chunks: list[str] = []
            header = getattr(page, "header", None)
            markdown = getattr(page, "markdown", None)
            footer = getattr(page, "footer", None)
            if header:
                page_chunks.append(str(header).strip())
            if markdown:
                page_chunks.append(str(markdown).strip())
            if footer:
                page_chunks.append(str(footer).strip())
            page_text = "\n".join([chunk for chunk in page_chunks if str(chunk).strip() != ""]).strip()
            if page_text == "":
                continue
            page_index = getattr(page, "index", None)
            if page_index is None:
                parts.append(page_text)
            else:
                parts.append("Page " + str(page_index) + "\n" + page_text)
        return "\n\n".join(parts).strip()

