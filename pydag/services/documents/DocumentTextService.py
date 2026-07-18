from dataclasses import dataclass, field
import os
from loguru import logger


from ...buffers.Buffer import Buffer
from ..ServiceException import ServiceException
from ..ReadService import ReadService
from ...agents.Agent import Agent
from ...buffers.ListBuffer import ListBuffer
from ...utils.FileUtils import FileUtils


@dataclass
class DocumentTextService(ReadService):
    """`MappingService` that retrieves text content from specified files
    
    """
    
    file_path : str = field(default=None, metadata={"description": "the path to a file or a folder, that shall be screened for document texts"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if not FileUtils.exists_file(self.file_path):
            raise ServiceException("file_path " + self.file_path + " does not exist or is a folder, please specify a valid file path")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
    
    def read_from_source(self):
        if len(self.get_buffers()) == 1 and len(self.addresses) == 0 and self.file_path is not None:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            if isinstance(buffer, ListBuffer):
                if os.path.isfile(self.file_path):
                    s = DocumentTextService.extract_text(self.file_path)
                    buffer.push(s)
                else:
                    raise ServiceException("file_path " + self.file_path + " must be a valid filepath (not a folder)")
            else:
                raise ServiceException("Only " + ListBuffer.cname() + "s are supported for this input combination of buffers and addresses")    
        elif len(self.get_buffers()) == len(self.addresses):
            raise ServiceException("Unsupported input combination with buffers and addresses")
        else:
            raise ServiceException("Unsupported input combination with buffers and addresses")
        
    @staticmethod
    def extract_text(file : str) -> str:
        if FileUtils.exists_file(file):
            _, ext = os.path.splitext(file)
            ext = ext.lower().replace(".", "")
            match ext:
                case "xlsx":
                    from unstructured.partition.xlsx import partition_xlsx

                    elements = partition_xlsx(file)
                case "docx":
                    from unstructured.partition.docx import partition_docx

                    elements = partition_docx(file)
                case "txt" | "csv" | "json":
                    from unstructured.partition.text import partition_text

                    elements = partition_text(file)
                case "pptx":
                    from unstructured.partition.pptx import partition_pptx

                    elements = partition_pptx(file)
                case "pdf":
                    from unstructured.partition.pdf import partition_pdf

                    elements = partition_pdf(file)
                case "html":
                    from unstructured.partition.html import partition_html

                    elements = partition_html(file)
                case "msg":
                    from unstructured.partition.email import partition_email

                    elements = partition_email(file)
                case "jpg" | "jpeg" | "png":
                    from unstructured.partition.image import partition_image

                    elements = partition_image(file)
                case _:
                    logger.warning("File Extension " + ext + " is not supported")
                    return None
            
            s = ""
            for element in elements:
                s = s + "\n" + element.text
            return s
        else:
            return None
