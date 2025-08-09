from dataclasses import dataclass, field
from ..buffers.Buffer import Buffer
from ..agents.Agent import Agent
from .Node import Node
from .StatemachineException import StatemachineException

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(init=True, default=None, metadata={"description": "unique ID of the buffer"})
    
    def __init__(self):
        super().__init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance
        
    def install(self, agent : Agent = None):
        """this `install` method connects a `Buffer` instance from specified `agent` based on given `buffer_id`

        Args:
            agent (agent, optional): agent instance. Defaults to None.

        Raises:
            StatemachineException: throws an `Exception` if no `buffer` with the specified `buffer_id` can be found in `agent`
        """
        super().install(agent)
        if self.buffer is None:
            if self.buffer_id in agent.buffer_store:
                self.buffer = agent.buffer_store[self.buffer_id]
            else:
                raise StatemachineException("No " + Buffer.cname() + " with id=" + self.buffer_id + " exists in " + Agent.cname())
        
    def deinstall(self, agent : Agent = None):
        super().deinstall(agent)
        self.buffer : Buffer = None
            