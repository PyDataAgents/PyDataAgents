from dataclasses import dataclass, field
import numpy as np

from ...adapters.AdapterException import AdapterException
from ...buffers.Buffer import Buffer
from ...buffers.ListBuffer import ListBuffer
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ...adapters.ReadAdapter import ReadAdapter


@dataclass
class NpzAdapter(ReadAdapter):
    """`Adapter` that retrieves data from a *.npz numpy file
    
    """
    
    file_path : str = field(default=None, metadata={"description": "the path to a file or a folder, that shall be screened for document texts"})
            
    def connect(self) -> bool:        
        return FileUtils.exists_file(self.file_path)
    
    def disconnect(self) -> bool:
        return True
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
        if len(buffers) == 1 and addresses is None:
            buffer : Buffer = next(iter(buffers.values()))
            if isinstance(buffer, DictBuffer):
                data = np.load(self.file_path)
                buffer.push(data)
            else:
                raise AdapterException("Only " + DictBuffer.cname() + "s are supported for this input combination of buffers and addresses")    
        elif len(buffers) == len(addresses) and len(addresses) > 0:
            a = 0
            for buffer in buffers.values():
                if isinstance(buffer, ListBuffer):
                    data = np.load(self.file_path)
                    list_data = data[addresses[a]]
                    buffer.push(list_data)
                    # TODO
                else:
                    raise AdapterException("Only " + ListBuffer.cname() + "s are supported for this input combination of buffers and addresses")
                a = a + 1
        else:
            raise AdapterException("Unsupported input combination with buffers and addresses")
        