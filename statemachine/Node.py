from __future__ import annotations
from dataclasses import dataclass, field
from PyDataGrabber.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.statemachine.State import State

@dataclass
class Node(GrabberElement):
    
    child_ids : list[str] = field(default=list(), metadata={"description" : "List of child node IDs"})
    
    def __init__(self):
        super().__init__()
        self.parents : list[Node] = list()
        self.children : list[Node] = list()
        self.state : State = State.INACTIVE
        
    def add_child(self, node : Node):
        self.children.append(node)
        node.parents.append(self)       
    