from dataclasses import dataclass, field
import numpy as np

from ...buffers.Buffer import Buffer
from ...utils.FileUtils import FileUtils
from ...utils.DataUtils import DataUtils
from ...buffers.DictBuffer import DictBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class ReadNpzAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the *.npz file to read the data from"})
    
    def _on_execute(self):
        if FileUtils.exists_file(self.file_path):
            if isinstance(self._buffer, DictBuffer):
                data = np.load(self.file_path)
                d = {key: DataUtils.ndarray_to_list(data[key]) for key in data.files}
                data.close()
                self.add_data(d)
            else:
                raise NodeException("only " + Buffer.cname() + "s of type " + DictBuffer.cname() + " are allowed")
        else:
            raise NodeException("filepath " + self.file_path + " does not exist")