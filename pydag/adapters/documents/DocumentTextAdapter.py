from dataclasses import dataclass, field
import os

from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.email import partition_email
from unstructured.partition.text import partition_text
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.image import partition_image

from pydag.adapters.AdapterException import AdapterException
from pydag.adapters.ReadAdapter import ReadAdapter
from pydag.buffers.Buffer import Buffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.utils.FileUtils import FileUtils

@dataclass
class DocumentTextAdapter(ReadAdapter):
    """`Adapter` that retrieves text content from specified files
    
    """
    
    file_path : str = field(default=None, metadata={"description": "the path to a file or a folder, that shall be screened for document texts"})
            
    def connect(self) -> bool:        
        return FileUtils.exists_file(self.file_path)
    
    def disconnect(self) -> bool:
        return True
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
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
                    elements = partition_xlsx(file)                                
                case "docx":
                    elements = partition_docx(file)
                case "txt" | "csv" | "json":
                    elements = partition_text(file)
                case "pptx":
                    elements = partition_pptx(file)
                case "pdf":
                    elements = partition_pdf(file)
                case "html":
                    elements = partition_html(file)
                case "msg":
                    elements = partition_email(file)
                case "jpg" | "jpeg" | "png":
                    elements = partition_image(file)
                case _:
                    DocumentTextAdapter.LOGGER.warning("File Extension " + ext + " is not supported")
                    return None
            
            s = ""
            for element in elements:
                s = s + "\n" + element.text
            return s
        else:
            return None