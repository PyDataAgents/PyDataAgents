from dataclasses import dataclass, field
from pydag.utils.DataUtils import DataUtils
from ...services.llm.LLMService import LLMService
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.utils.DataUtils import DataUtils
import os
from openai import OpenAI
import configparser
from ..BufferNode import BufferNode
from ..Action import Action
from ...agents.Agent import Agent


@dataclass
class LLMImageAnalysisAction(BufferNode, Action):
    """ `Action` to retrieve information from an image and store the response in its `Buffer`.
    The Action analyses arbitrary images for its content (not only text documents like OCR). Hence it is powerful for image understanding tasks. 
    If you specifically want to extract text as well as its formatting from images, consider using the LLMOCRAction instead.
    The parent Buffer Node is expected to provide file paths to images or PDFs.
    The allowed inpus formats for the file paths are:
    - A fully qualified file path as a string
    - an image as a Base64-encoded data URL 
    - For OpanAI models: a file ID (created with the Files API (https://platform.openai.com/docs/api-reference/files))
    The OpenAI API is used.
    Keep in mind that the provided model must support image inputs, e.g. for OpenAI use "gpt-4o" or "gpt-4o-mini" or "gpt-4.1-mini" or "gpt-4.1" or "gpt-5".
    For more models and providers refer to their documentation, e.g. OpenAI: https://platform.openai.com/docs/models".

    The output has the following format:
    {
        "question": <the question asked>,
        "answer": <the answer from the LLM>
        "filepath": <file path for each processed input>
    }

    """

    template: str = field(default=None, metadata={"description": "Not in use for the LLMOCRAction, as the message format is fixed for image inputs."})
    output_keys : list[str] = field(default_factory=lambda: ["question", "answer", "filepath"])
    question: str = field(default=" ", metadata={"description": "The question to ask the LLM about the image content."})
    

    def _on_install(self, agent : Agent = None):
        BufferNode._on_install(self, agent)        
        _config = configparser.ConfigParser()
        _config.read("config.ini")
        self.client = OpenAI(api_key=_config["OPENAI"]["OPENAI_API_KEY"])

    def _on_execute(self):
          
        """
        Usage with templates (not implemented yet and must be adaptet to the message format for images):
        """
        """
        # check if template and data keys match
        # Match with either the occurences of a number inside {}, or empty {}
        if self.template is not None:
            empty_brackets = self.template.count("{}")
            number_brackets = len(set(re.findall(r'\{\d+\}', self.template)))
        else:
            empty_brackets = -1
            number_brackets = -1
        if len(self.input_keys) == empty_brackets or len(self.input_keys) == number_brackets or self.template is None:            
            data = self.get_parent_data()
            rows = DataUtils.dict_to_list(data)
            for row in rows:
                if self.template is None:
                    question = " ".join([str(x) for x in row.values()])
                else:
                    question = self.template.format(*row.values())
                
                if isinstance(self._service, LLMService):
                    answer = self._service.chat(question)
                    dic = dict(zip(self.output_keys, [question, answer]))
                    self._buffer.push(dic)
        else:
            raise NodeException(f"number of input_keys({len(self.input_keys)}) and placeholders ({self.template.count('{}')}) in template do not match")
        """   
        self.template = None  # not in use for image inputs       
        data = self.get_parent_data()
        rows = DataUtils.dict_to_list(data)
        if rows is None:
            return
        for row in rows:
            if self.template is None:
                _image = " ".join([str(x) for x in row.values()])
                _image_path = None
                # check file type
                # check if _image is a file path
                if os.path.isfile(_image):
                    _image_path = _image
                    _image = DataUtils.image_to_base64(_image)
                    # Ensure that _image is a valid image MIME type
                    if not any(_image.startswith(prefix) for prefix in ["data:image/", "data:application/pdf", "data:video/"]):
                        continue # skip non-image files
                elif _image.strip() == "":
                    continue # skip empty values
                
                else:
                    # assume it is already a base64 data URL or a file ID
                    pass
                
                _message = [{
                                    "role": "system",
                                    "content": [
                                    {
                                        "type": "input_text",
                                        "text": (
                                        "You are an image explanation engine. Your job is to describe images with maximum fidelity.\n\n"
                                        "Rules (must follow):\n"
                                        """
                                        1) Prioritize factual content over interpretation.
                                        2) Include concrete details: subjects, colors, shapes, materials, textures, positions, counts (when clear), spatial relationships, lighting, focus/blur, and overall composition.
                                        3) Avoid named entities/brands/identities unless explicitly readable in the image.
                                        4) Never mention objects or attributes that are not clearly present.
                                        5) If mainly text-based, follow the below OCR-guidelines instead:

                                        Output format (use headings):
                                        - Overall summary (1–3 sentences)
                                        - Scene/setting
                                        - Main subjects (detailed)
                                        - Secondary objects/details
                                        - Lighting/color/image qualities
                                        - Composition/framing
                                        - Readable text
                                        """
                                        "OCR Guidelines (if image is text-based) which MUST be obeyed:\n"
                                        "1) Output ONLY the answer on the provided question as consice as possible! — no explanations, no commentary, no markdown, no code fences.\n"
                                        "2) Transcribe verbatim: preserve original spelling, casing, punctuation, symbols, and numbers.\n"
                                        "3) Preserve layout as plain text: keep line breaks, paragraph breaks, and approximate spacing/indentation when visible.\n"
                                        "4) Maintain reading order top-to-bottom, left-to-right. For multi-column layouts, fully transcribe the left column then the next.\n"
                                        "5) Do NOT infer or correct. If uncertain, keep the most likely characters; if unreadable, use [ILLEGIBLE].\n"
                                        "6) If some text is cut off, include the visible portion and append [TRUNCATED].\n"
                                        "7) Ignore non-text visual details unless they are part of the text (e.g., icons with labels).\n"
                                        "8) If there is no text, output exactly: [NO TEXT]."
                                        )
                                    }
                                    ],
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "input_text", "text": f"{self.question}"},
                                        {
                                            "type": "input_image",
                                            "image_url": _image
                                        },
                                    ],
                                }
                            ]
           

            resp = self.client.responses.create(
                model="gpt-4.1-mini",
                input=_message)
            #answer = resp.output_text if isinstance(resp.output_text, list) else [resp.output_text]
            answer = resp.output_text
            # check if answer is empty
            if len(answer) == 0:
                return
            dic = dict(zip(self.output_keys, [str(_message), answer, _image_path]))
            self.add_data(dic)

