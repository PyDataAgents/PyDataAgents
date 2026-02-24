from dataclasses import dataclass, field
from ...utils.DataUtils import DataUtils
from ...utils.DataUtils import DataUtils
import os
import configparser
from loguru import logger


from ...nodes.BufferNode import BufferNode
from ...nodes.Action import Action
from ...agents.Agent import Agent
from mistralai import Mistral


@dataclass
class LLMOCRAction(BufferNode, Action):
    """ `Action` to retrieve text from an image or PDF and store the extracted text in its `Buffer`.
    The parent Buffer Node is expected to provide file paths to images or PDFs.
    The allowed input formats for the file paths are:
    - A fully qualified file path as a string
    - an image as a Base64-encoded data URL 
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

    """

    api_key : str = field(default=None, metadata={"description": "a mistral ai api key"})
    output_keys : list[str] = field(default_factory=lambda: ["documents", "filepath"])
    
    def __post_init__(self):
        super().__post_init__()
        self._client : Mistral = None

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._client = Mistral(api_key=self.api_key)

    def _on_execute(self):    
        data = self.get_parent_data()
        rows = DataUtils.dict_to_list(data)
        for row in rows:
            _image = " ".join([str(x) for x in row.values()])
            _image_path = None
            _image_type = _image.split(".")[-1].lower()
            # check file type
            # check if _image is a file path
            if os.path.isfile(_image):
                _image_path = _image
                _image = DataUtils.image_to_base64(_image)
                if _image is None:
                    continue
                # Ensure that _image is a valid image MIME type
                if not _image_type in ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]+["pdf", "docx", "pptx","txt", "odt", "bib", "tex", "rtf", "md", "html", "xlsx", "csv"]:
                    continue # skip non-text files
            elif _image.strip() == "":
                continue # skip empty values        
            else:
                # assume it is already a base64 data URL or a file ID
                # and check for image type if its a base64 string already
                if "data:image/" in _image:
                    _image_type = _image.split("data:image/")[1].split(";base64")[0]
                else:
                    logger.debug("could not detect data URI for base64 image url")
                    continue        
            if _image_type in ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]:
                resp = self._client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "image_url",
                            "image_url":  f"{_image}"
                        },
                        #table_format="markdown",
                        # extract_header=True, # default is False
                        # extract_footer=True, # default is False
                        include_image_base64=True
                    )
            elif _image_type in ["pdf"]:
                resp = self._client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "document_url",
                            "document_url": f"{_image}"
                        },
                        #table_format="markdown",
                        # extract_header=True, # default is False
                        # extract_footer=True, # default is False
                        include_image_base64=True
                    )
            else:
                continue # skip unsupported file types
            answer = str([str(p) for p in resp.pages])
            dic = dict(zip(self.output_keys, [str(answer), _image_path]))
            self.add_data(dic)

