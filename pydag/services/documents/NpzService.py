from dataclasses import dataclass, field
import numpy as np


from ...agents.Agent import Agent
from ...utils.DataUtils import DataUtils
from ..ServiceException import ServiceException
from ...buffers.Buffer import Buffer
from ...buffers.ListBuffer import ListBuffer
from ...buffers.DictBuffer import DictBuffer
from ...utils.FileUtils import FileUtils
from ..ReadService import ReadService


@dataclass
class NpzService(ReadService):
    """`Adapter` that retrieves data from a *.npz numpy file
    
    """
    
    file_path : str = field(default=None, metadata={"description": "the path to a file or a folder, that shall be screened for document texts"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if not FileUtils.exists_file(self.file_path):
            raise ServiceException("file_path " + self.file_path + " does not exist or is a folder, please specify a valid file path")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
                
    def _read_from_source(self):
        if len(self.get_buffers()) == 1 and len(self.addresses) == 0:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            if isinstance(buffer, DictBuffer):
                data = NpzService.__extract_npz_data(self.file_path)
                buffer.push(data)
            else:
                raise ServiceException("Only " + DictBuffer.cname() + "s are supported for this input combination of buffers and addresses")    
        elif len(self.get_buffers()) == len(self.addresses) and len(self.addresses) > 0:
            a = 0
            for buffer in self.get_buffers().values():
                if isinstance(buffer, ListBuffer):
                    data = NpzService.__extract_npz_data(self.file_path)
                    buffer.push(data[self.addresses[a]])
                else:
                    raise ServiceException("Only " + ListBuffer.cname() + "s are supported for this input combination of buffers and addresses")
                a = a + 1
        else:
            raise ServiceException("Unsupported input combination with buffers and addresses")
    
    @staticmethod    
    def __extract_npz_data(file_path : str) -> dict:
        data = np.load(file_path)
        d = {key: DataUtils.ndarray_to_list(data[key]) for key in data.files}
        data.close()
        return d