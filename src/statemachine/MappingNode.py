from dataclasses import dataclass, field

from PyDataGrabber.src.statemachine.Node import Node

@dataclass
class MappingNode(Node):
    
    mapping_id: str = field(default=None, metadata={"description": "ID of the mapping"})    
    
    def __init__(self):
        super().__init__()
        self.mapping = None