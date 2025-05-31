from dataclasses import dataclass, field

from ..grabbers.Grabber import Grabber
from ..mappings.MappingThread import MappingThread
from .Node import Node
from .StatemachineException import StatemachineException

@dataclass
class MappingNode(Node):
    
    mapping_id: str = field(default=None, metadata={"description": "ID of the mapping"})    
    
    def __init__(self):
        super().__init__()
        self.mapping_thread : MappingThread = None
        
    def install(self, grabber : Grabber = None):
        super().install()
        if self.mapping_thread is None:
            if self.mapping_id in grabber.mapping_store:
                self.mapping_thread = grabber.mapping_store[self.mapping_id]
            else:
                raise StatemachineException("No " + MappingThread.cname() + " with id=" + self.mapping_id + " was found")
            
    def deinstall(self, grabber : Grabber = None):
        super().deinstall()
        self.mapping_thread : MappingThread = None