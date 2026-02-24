from dataclasses import dataclass, field
from ..adapters.Adapter import Adapter
from ..agents.Agent import Agent
from .BufferNode import BufferNode
from ..services.statemachine.StatemachineException import StatemachineException

@dataclass
class AdapterNode(BufferNode):
    """
    AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
    It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
    """
    
    adapter_id: str = field(init=True, default=None, metadata={"description": "ID of the adapter"})

    def __post_init__(self):
        super().__post_init__()
        self._adapter : Adapter = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self._adapter is None:
            if agent.get_adapter(self.adapter_id):
                self._adapter = agent.get_adapter(self.adapter_id)
            else:
                raise StatemachineException("No " + Adapter.cname() + " with id=" + self.adapter_id + " was found in " + agent.cname())
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._adapter = None
