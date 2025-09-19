from __future__ import annotations
from dataclasses import dataclass, field
from ..agents.AgentElement import AgentElement
from .State import State

@dataclass
class Node(AgentElement):
    
    child_ids : list[str] = field(init=True, default_factory=list, metadata={"description" : "List of child node IDs"})
    
    def __post_init__(self):
        super().__post_init__()
        self.parents : list[Node] = list()
        self.children : list[Node] = list()
        self.state : State = State.INACTIVE
        self.child_ids = list[str]()
      
    def add_child(self, child : Node):
        self.children.append(child)
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)
        child.parents.append(self)
        
    def add_parent(self, parent : Node):
        self.parents.append(parent)
        parent.children.append(self)
        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)
    