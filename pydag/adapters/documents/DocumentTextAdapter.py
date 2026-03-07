from dataclasses import dataclass, field
import os
from loguru import logger

from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...agents.Agent import Agent
from ...buffers.Buffer import Buffer
from ...buffers.ListBuffer import ListBuffer
from ...utils.FileUtils import FileUtils

@dataclass
class DocumentTextAdapter(ReadAdapter):
    """`Adapter` that retrieves text content from specified files
    
    """
    
    file_path : str = field(default=None, metadata={"description": "the path to a file or a folder, that shall be screened for document texts"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
            
    def _on_connect(self) -> bool:        
        return FileUtils.exists_file(self.file_path)
    
    def _on_disconnect(self) -> bool:
        return True
    
    def _on_read(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
        if len(buffers) == 1 and len(addresses) == 0 and self.file_path is not None:
            buffer : Buffer = next(iter(buffers.values()))
            if isinstance(buffer, ListBuffer):
                if os.path.isfile(self.file_path):
                    s = DocumentTextAdapter.extract_text(self.file_path)
                    buffer.push(s)
                else:
                    raise AdapterException("file_path " + self.file_path + " must be a valid filepath (not a folder)")
            else:
                raise AdapterException("Only " + ListBuffer.cname() + "s are supported for this input combination of buffers and addresses")    
        elif len(buffers) == len(addresses):
            raise AdapterException("Unsupported input combination with buffers and addresses")
        else:
            raise AdapterException("Unsupported input combination with buffers and addresses")
    
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
