from dataclasses import dataclass, field

from loguru import logger

from pydag.utils.DataUtils import DataUtils

from ...agents.AgentConfig import AgentConfig
from ...agents.Agent import Agent
from ...buffers.DataType import DataType
from ...buffers.ListBuffer import ListBuffer
from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class ConvertFile2Base64Action(BufferNode, Action):
    
    file_paths : list[str] = field(default_factory=list, metadata={"description": "path to the file to convert to base64, e.g. PNG | JPG | PDF | MP4 | AVI | MOV | MP3"})
        
    def _on_install(self, agent : Agent = None):
        if len(self.input_keys) == 0 and len(self.file_paths) == 0:
            raise NodeException("Whether file_paths nor input_keys was specified")
        if self._buffer is None:
            if agent is not None:
                buf = agent.get_buffer(self.buffer_id)                
                if buf:
                    self._buffer = buf
                else:
                    self._buffer = ListBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY, data_type=DataType.STRING.value)
                    self.buffer_id = self._buffer.id
                    if self.file_paths:
                        self._buffer.capacity = len(self.file_paths)
                    self._buffer.install(agent)
                    agent.add_buffer(self._buffer)
            else:
                self._buffer = ListBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY, data_type=DataType.STRING.value)
                if self.file_paths:
                    self._buffer.capacity = len(self.file_paths)
                self.buffer_id = self._buffer.id
                self._buffer.install(agent)
    
    def _on_execute(self):
        file_paths : list[str] = []                
        if len(self.input_keys) > 0:
            if len(self._parents) > 0:
                data = self.get_parent_data()
                for d in data.values():
                    if isinstance(d, list):
                        file_paths.extend(d)
                    elif isinstance(d, str):
                        file_paths.append(d)
            else:
                raise NodeException("this node has no parents")
        else:
            file_paths = self.file_paths        
        if len(file_paths) > 0:
            for file_path in file_paths:
                if FileUtils.exists_file(file_path):
                    b64 = DataUtils.image_to_base64(file_path)
                    if b64:
                        self.add_data(b64)
                else:
                    logger.error("File '" + file_path + "' could not be found!")
        else:
            raise NodeException("no filepaths were specified or retrieved")