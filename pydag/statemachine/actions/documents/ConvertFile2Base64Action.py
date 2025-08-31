import base64
from dataclasses import dataclass, field

from loguru import logger 

from ....agents.Agent import Agent
from ....buffers.DataType import DataType
from ....buffers.ListBuffer import ListBuffer
from ....statemachine.NodeException import NodeException
from ....utils.FileUtils import FileUtils
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class ConvertFile2Base64Action(BufferNode, Action):
    
    file_paths : list[str] = field(default_factory=list, metadata={"description": "path to the file to convert to base64, e.g. PNG | JPG | PDF | MP4 | AVI | MOV | MP3"})
    extract_parent_keys : list[str] = field(default_factory=list, metadata={"description": "instead of directly specifying file_paths, this property can be used to retrieve the filepaths from a parent buffer"})
        
    def install(self, agent : Agent = None):
        if len(self.extract_parent_keys) == 0 and len(self.file_paths) == 0:
            raise NodeException("Whether file_paths nor extract_parent_keys was specified")
        Action.install(self, agent)
        if self.buffer is None:
            if agent is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
                else:
                    self.buffer = ListBuffer(id=self.id + "-BUFFER", capacity=len(self.file_paths), data_type=DataType.STRING.value)
                    self.buffer_id = self.buffer.id
                    self.buffer.install(agent)
                    agent.add_buffer(self.buffer)
            else:
                self.buffer = ListBuffer(id=self.id + "-BUFFER", capacity=len(self.file_paths), data_type=DataType.STRING.value)
                self.buffer_id = self.buffer.id
                self.buffer.install(agent)
    
    def execute(self):
        file_paths : list[str] = []                
        if len(self.extract_parent_keys) > 0:
            if len(self.parents) > 0:
                has_buffers = False
                for parent in self.parents:
                    if isinstance(parent, BufferNode):
                        has_buffers = True
                        data = parent.buffer.data(persistent=False)
                        for key in self.extract_parent_keys:
                            if key in data:
                                file_paths.append(data[key])
                if not has_buffers:
                    raise NodeException("this node has no parents of type " + BufferNode.cname())
            else:
                raise NodeException("this node has no parents")
        else:
            file_paths = self.file_paths        
        if len(file_paths) > 0:
            for file_path in self.file_paths:
                if FileUtils.exists_file(file_path):
                    with open(file_path, 'rb') as file:
                        encoded = base64.b64encode(file.read())
                        base64_string = encoded.decode('utf-8')
                        self.buffer.push(base64_string)
                else:
                    logger.error("File '" + file_path + "' could not be found!")
        else:
            raise NodeException("no filepaths were specified or retrieved")