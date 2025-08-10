from dataclasses import dataclass, field
import numpy as np

from pydag.utils.DataUtils import DataUtils

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
        if len(buffers) == 1 and len(addresses) == 0:
            buffer : Buffer = next(iter(buffers.values()))
            if isinstance(buffer, DictBuffer):
                data = NpzAdapter.__extract_npz_data(self.file_path)
                buffer.push(data)
            else:
                raise AdapterException("Only " + DictBuffer.cname() + "s are supported for this input combination of buffers and addresses")    
        elif len(buffers) == len(addresses) and len(addresses) > 0:
            a = 0
            for buffer in buffers.values():
                if isinstance(buffer, ListBuffer):
                    data = NpzAdapter.__extract_npz_data(self.file_path)
                    buffer.push(data[addresses[a]])
                else:
                    raise AdapterException("Only " + ListBuffer.cname() + "s are supported for this input combination of buffers and addresses")
                a = a + 1
        else:
            raise AdapterException("Unsupported input combination with buffers and addresses")
    
    @staticmethod    
    def __extract_npz_data(file_path : str) -> dict:
        data = np.load(file_path)
        d = {key: DataUtils.ndarray_to_list(data[key]) for key in data.files}
        data.close()
        return d