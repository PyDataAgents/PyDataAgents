from __future__ import annotations
from dataclasses import dataclass, field
from ..grabbers.GrabberElement import GrabberElement
from .State import State

@dataclass
class Node(GrabberElement):
    
    child_ids : list[str] = field(init=True, default_factory=list, metadata={"description" : "List of child node IDs"})
    
    def __init__(self):
        super().__init__()
        self.parents : list[Node] = list()
        self.children : list[Node] = list()
        self.state : State = State.INACTIVE
        self.child_ids = list[str]()
      
    def add_child(self, child : Node):
        self.children.append(child)
        child.parents.append(self)
        
    def add_parent(self, parent : Node):
        self.parents.append(parent)
        parent.children.append(self)     
    