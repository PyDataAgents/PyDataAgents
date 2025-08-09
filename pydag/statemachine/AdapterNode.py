from dataclasses import dataclass, field
from ..adapters.Adapter import Adapter
from ..agents.Agent import Agent
from .BufferNode import BufferNode
from .StatemachineException import StatemachineException

@dataclass
class AdapterNode(BufferNode):
    """
    AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
    It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
    """
    
    adapter_id: str = field(init=True, default=None, metadata={"description": "ID of the adapter"})

    def __post_init__(self):
        super().__post_init__()
        self.adapter : Adapter = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if self.adapter is None:
            if self.adapter_id in agent.adapter_store:
                self.adapter = agent.adapter_store[self.adapter_id]
            else:
                raise StatemachineException("No " + Adapter.cname() + " with id=" + self.adapter_id + " was found in " + agent.cname())
    
    def deinstall(self, agent : Agent = None):
        super().deinstall(agent)
        self.adapter = None
