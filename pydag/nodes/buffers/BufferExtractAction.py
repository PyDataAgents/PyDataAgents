from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ...buffers.Buffer import Buffer
from ...buffers.DictBuffer import DictBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class BufferExtractAction(BufferNode, Action):
    """
    `Action` for extracting data from a specified buffer and to store the extracted data into this buffer.
    This `Action` can only be applied on if the specified buffer is of type `DictBuffer`.
    """
    
    extract_buffer_id : str = field(default=None, metadata={"description": "id of the buffer to extract data from"})    
    
    def __post_init__(self):
        super().__post_init__()
        self._extract_buffer : Buffer = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if agent is not None:
            if self._extract_buffer is None:
                if agent.get_buffer(self.extract_buffer_id):
                    self._extract_buffer = agent.get_buffer(self.buffer_id)
                else:
                    raise NodeException("No " + Buffer.cname() + " with id=" + self.extract_buffer_id + " exists in " + Agent.cname())
            
    def _on_execute(self):
        if not isinstance(self._extract_buffer, DictBuffer):
            raise NodeException("specified buffer must be of type " + DictBuffer.cname())
        d = {}
        for key in self.input_keys:
            bd = self._extract_buffer.data(n=self.n, persistent=self.persistent)
            if bd is not None:
                if key in bd:
                    d[key] = bd[key]
        if len(d) > 0:
            self.add_data(d)
                        
    def set_extract_buffer(self, buffer : Buffer):
        self._extract_buffer = buffer
        self.extract_buffer_id = buffer.id
            
                  
                        
                    
    