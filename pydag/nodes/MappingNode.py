from dataclasses import dataclass, field

from ..agents.Agent import Agent
from ..mappings.MappingThread import MappingThread
from .Node import Node
from ..services.statemachine.StatemachineException import StatemachineException

@dataclass
class MappingNode(Node):
    
    mapping_id: str = field(init=True, default=None, metadata={"description": "ID of the mapping"})    
    
    def __post_init__(self):
        super().__post_init__()
        self.mapping_thread : MappingThread = None
        
    def install(self, agent : Agent = None):
        super().install()
        if self.mapping_thread is None:
            if self.mapping_id in agent.mapping_store:
                self.mapping_thread = agent.mapping_store[self.mapping_id]
            else:
                raise StatemachineException("No " + MappingThread.cname() + " with id=" + self.mapping_id + " was found")
            
    def deinstall(self, agent : Agent = None):
        super().deinstall()
        self.mapping_thread : MappingThread = None