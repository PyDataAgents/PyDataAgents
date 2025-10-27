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
    extract_keys : list[str] = field(default_factory=list, metadata={"description": "keys to search for in the specified buffer and extract their values into this element's buffer"})
    
    def __post_init__(self):
        super().__post_init__()
        self.extract_buffer : Buffer = None
    
    def install(self, agent : Agent = None):
        super().install(agent)
        if agent is not None:
            if self.extract_buffer is None:
                if self.extract_buffer_id in agent.buffer_store:
                    self.extract_buffer = agent.buffer_store[self.buffer_id]
                else:
                    raise NodeException("No " + Buffer.cname() + " with id=" + self.extract_buffer_id + " exists in " + Agent.cname())
            
    def execute(self):
        if not isinstance(self.extract_buffer, DictBuffer):
            raise NodeException("specified buffer must be of type " + DictBuffer.cname())
        d = {}
        for key in self.extract_keys:
            bd = self.extract_buffer.data(n=self.n, persistent=self.persistent)
            if bd is not None:
                if key in bd:
                    d[key] = bd[key]
        if len(d) > 0:
            self.buffer.push(d)
            
                  
                        
                    
    