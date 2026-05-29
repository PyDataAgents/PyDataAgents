from dataclasses import dataclass, field
import shutil
from pdf2image import convert_from_path
import pytesseract
from PIL import Image


from pydag.agents.Agent import Agent
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException
from pydag.utils.FileUtils import FileUtils

@dataclass
class OCRAction(BufferNode, Action):
    """ `Action` to perform OCR on images or pdfs that loaded from filepaths of parent `BufferNode`s and stored as extracted text in its `Buffer`.
    
    the action outputs extracted text and the source path with the keys ["path", "text"]
    
    Requirements:
    - make sure poopler is installed and on PATH (in windows)
    https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0
    - make sure tesseract is installed and on PATH (in windows)
    https://tesseract-ocr.github.io/tessdoc/Installation.html and https://github.com/UB-Mannheim/tesseract/wiki (for windows)
    """
    
    path_key : str = field(default="path", metadata={"description": "Key for the source file path in the output dictionary."})
    text_key : str = field(default="text", metadata={"description": "Key for text output in the output dictionary."})
    
    def _on_install(self, agent : Agent = None):
        BufferNode._on_install(self, agent)
        # check if binaries are installed
        if shutil.which("tesseract") is None or shutil.which("pdfinfo") is None or shutil.which("pdftoppm") is None:
            raise NodeException("Tesseract and Poppler must be installed and on PATH to use OCRAction.")
        
    def _on_execute(self):
        data = self.get_parent_data()
        for k, d in data.items():
            if len(d)> 0:
                # check if dd contains filepaths
                if FileUtils.exists_file(d[0]):
                    fp : str
                    for fp in d:
                        if ".pdf" in fp.lower():
                            # process pdf
                            s = OCRAction.process_pdf(fp)
                            dic = {self.path_key: fp, self.text_key: s}
                            self.add_data(dic)
                        else:
                            # process image
                            s = OCRAction.process_image(fp)
                            dic = {self.path_key: fp, self.text_key: s}
                            self.add_data(dic)            
    
    @staticmethod
    def process_pdf(pdf_path : str) -> str:
        """Helper method to process an pdf file and extract text using OCR.

        Args:
            pdf_path (str): Path to the pdf file.
        """
        pages = convert_from_path(pdf_path)
        all_text = ""
        for page in pages:
            text = pytesseract.image_to_string(page)
            all_text += text + "\n"
        return all_text
    
    @staticmethod
    def process_image(image_path : str) -> str:
        """Helper method to process an image file and extract text using OCR.

        Args:
            image_path (str): Path to the image file.
        """
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
                        