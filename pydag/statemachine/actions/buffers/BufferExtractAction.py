from dataclasses import dataclass, field

from ....agents.Agent import Agent
from ....buffers.Buffer import Buffer
from ....buffers.DictBuffer import DictBuffer
from ...StatemachineException import StatemachineException
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class BufferExtractAction(BufferNode, Action):
    """
    `Action` for extracting data from a specified buffer and to store the extracted data into this buffer.
    This `Action` can only be applied on if the specified buffer is of type `DictBuffer`.
    """
    
    extract_buffer_id : str = field(default=None, metadata={"description": "id of the buffer to extract data from"})    
    extract_keys : list[str] = field(default_factory=list, metadata={"description": "keys to search for in the specified buffer and extract their values into this element's buffer"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether to keep the extracted data in origin buffer"})
    n : int = field(default=0, metadata={"description": "number of samples to extract from buffer, default 0 extracts all"})
    
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
                    raise StatemachineException("No " + Buffer.cname() + " with id=" + self.extract_buffer_id + " exists in " + Agent.cname())
            
    def execute(self):
        if not isinstance(self.extract_buffer, DictBuffer):
            raise StatemachineException("specified buffer must be of type " + DictBuffer.cname())
        d = {}
        for key in self.extract_keys:
            bd = self.extract_buffer.data(n=self.n, persistent=self.persistent)
            if key in bd:
                d[key] = bd[key]
        self.buffer.push(d)
            
                  
                        
                    
    