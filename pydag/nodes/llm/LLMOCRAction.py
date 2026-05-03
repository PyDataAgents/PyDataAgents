from dataclasses import dataclass, field
from ...utils.DataUtils import DataUtils
import os
from loguru import logger





from ...nodes.BufferNode import BufferNode
from ...nodes.Action import Action
from ...agents.Agent import Agent


@dataclass
class LLMOCRAction(BufferNode, Action):
    """ `Action` to retrieve text from an image or PDF and store the extracted text in its `Buffer`.
    The parent Buffer Node is expected to provide file paths to images or PDFs.
    The allowed input formats for the file paths are:
    - A fully qualified file path as a string
    - an image as a Base64-encoded data URL 
    The Mistral OCR-3 model is used to extract text from the images or PDFs.
    For more information about the Mistral OCR-3 model: https://mistral.ai/news/mistral-ocr-3".

    The output has the following format in case of Mistral OCR-3 model:
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
    
        
    The output has the following format in case of the zai glm-ocr model:


    See https://docs.mistral.ai/capabilities/document_ai/basic_ocr for more details on the latest Mistral OCR model and https://arxiv.org/pdf/2603.10910 for the glm-ocr model.

    """

    api_key : str = field(default=None, metadata={"description": "an ai api key, e.g. for Mistral OCR"})
    output_keys : list[str] = field(default_factory=lambda: ["documents", "filepath"])
    model : str = field(default="mistral-ocr-latest", metadata={"description": "The model name. Either 'mistral-ocr-latest' for the lastest Mistral model or 'glm-ocr' for the zai OCR model (https://ollama.com/library/glm-ocr)."})
    include_image_base64 : bool = field(default=False, metadata={"description": "Whether OCR page payloads should include embedded base64 images"})
    
    def __post_init__(self):
        super().__post_init__()
        self._client = None

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)

        if self.model == "mistral-ocr-latest":
            from mistralai import Mistral
            self._client = Mistral(api_key=self.api_key)
        elif self.model == "glm-ocr":
            from ollama import chat
            from ollama import ResponseError
            self._client = chat
            self._ResponseError = ResponseError
        else:
            raise ValueError("Unsupported model: " + str(self.model))


    def _on_execute(self):    
        data = self.get_parent_data()
        rows = DataUtils.dict_to_list(data)
        for row in rows:
            image_ref = " ".join([str(x) for x in row.values()]).strip()
            if image_ref == "":
                continue
            document_payload, image_path, image_ref = self._resolve_document_payload(image_ref)
            
            # Mistral OCR
            if self.model == "mistral-ocr-latest":
                if document_payload is None:
                    continue
                resp = self._client.ocr.process(
                    model=self.model,
                    document=document_payload,
                    include_image_base64=self.include_image_base64,
                )
                answer = self._serialize_mistral_ocr_response(resp)
                dic = dict(zip(self.output_keys, [answer, image_path]))
                self.add_data(dic)
            
            # glm-ocr via ollama
            elif self.model == "glm-ocr":
                responses = []
                try:
                    image_ref = [_image.split(",", 1)[1] for _image in image_ref]
                    for _img in image_ref:
                        message = {"role":"user",
                            "images": [_img] 
                            }
                        resp = self._client(model="glm-ocr", messages=[message])
                        responses.append(resp)
                    answer = self._serialize_ollama_ocr_response(responses)
                    dic = dict(zip(self.output_keys, [answer, image_path]))
                    self.add_data(dic)
                except self._ResponseError as e:
                    if e.status_code == 404:
                        print(f"Model {self.model} not found locally. Pulling now...")
                        import ollama
                        ollama.pull(self.model)
                        image_ref = [_image.split(",", 1)[1] for _image in image_ref]
                        for _img in image_ref: 
                            message = {"role":"user",
                            "images": [_img] 
                            } 
                            resp = self._client(model="glm-ocr", messages=[message])
                            responses.append(resp)
                        answer = self._serialize_ollama_ocr_response(responses)
                        dic = dict(zip(self.output_keys, [answer, image_path]))
                        self.add_data(dic)
                    else:
                        raise 
            else:
                raise ValueError("Unsupported model: " + str(self.model))

            
            

    def _resolve_document_payload(self, image_ref: str):
        image_path = None
        image_type = image_ref.split(".")[-1].lower()
        if os.path.isfile(image_ref):
            image_path = image_ref
            image_ref = DataUtils.image_to_base64(image_ref)
            if image_ref is None:
                return None, None
        elif "data:image/" in image_ref:
            image_type = image_ref.split("data:image/")[1].split(";base64")[0]
        elif image_ref.startswith("data:application/pdf"):
            image_type = "pdf"
        else:
            logger.debug("could not detect supported OCR input: " + str(image_ref)[:120])
            return None, None

        if image_type in ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]:
            return {
                "type": "image_url",
                "image_url": str(image_ref),
            }, image_path, image_ref
        if image_type == "pdf":
            if self.model == "mistral-ocr-latest":
                return {
                    "type": "document_url",
                    "document_url": str(image_ref),
                }, image_path, image_ref
            if self.model == "glm-ocr":
                return {
                    "type": "document_url",
                    "document_url": str(image_ref),
                }, image_path, DataUtils.pdf_base64_to_image_base64(image_ref)

        return None, None, None

    
    def _serialize_ollama_ocr_response(self, response) -> str:
        def get_value(obj, key, default=None):
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            getter = getattr(obj, "get", None)
            if callable(getter):
                try:
                    return getter(key, default)
                except TypeError:
                    try:
                        return getter(key)
                    except Exception:
                        pass
            return getattr(obj, key, default)

        def response_content(obj):
            message = get_value(obj, "message")
            content = get_value(message, "content")
            if content is None:
                content = get_value(obj, "content")
            if content is None:
                return ""
            if isinstance(content, list):
                return "\n".join([str(chunk).strip() for chunk in content if str(chunk).strip() != ""]).strip()
            return str(content).strip()

        if not isinstance(response, list):
            return response_content(response)

        parts: list[str] = []
        for i, page_response in enumerate(response):
            page_content_str = response_content(page_response)
            if page_content_str == "":
                continue
            parts.append("Page " + str(i) + "\n" + page_content_str)
        return "\n\n".join(parts).strip()
    
    
    
    
    
    def _serialize_mistral_ocr_response(self, response) -> str:
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

