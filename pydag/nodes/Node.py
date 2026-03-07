from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


from ..agents.AgentStates import AgentElementState, NodeState
from ..agents.AgentElement import AgentElement

@dataclass
class Node(AgentElement):
    
    child_ids : list[str] = field(default_factory=list, metadata={"description" : "List of child node IDs"})
    
    def __post_init__(self):
        super().__post_init__()
        self._parents : list[Node] = list()
        self._children : list[Node] = list()
        self._is_active : bool = True
        self._state : Union[AgentElementState, NodeState] = AgentElementState.UNINSTALLED
        self._last_activation : int = 0
      
    def add_child(self, child : Node):
        self._children.append(child)
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)
        child.get_parents().append(self)
        
    def add_parent(self, parent : Node):
        self._parents.append(parent)
        parent.get_children().append(self)
        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)
    
    def get_parents(self) -> list[Node]:
        return self._parents
    
    def get_children(self) -> list[Node]:
        return self._children
    
    def is_active(self) -> bool:
        return self._is_active
    
    def set_active(self, active : bool):
        self._is_active = active
            
    def has_child(self, id : str) -> bool:
        """ returns True/False whether this `Node` has a child with `id`

        Args:
            id (str): unique id

        Returns:
            bool: True/False
        """
        for node in self._children:
            if node.id == id:
                return True
        return False
    
    def has_parent(self, id : str) -> bool:
        """ returns True/False whether this `Node` has a parent with `id`

        Args:
            id (str): unique id

        Returns:
            bool: True/False
        """
        for node in self._parents:
            if node.id == id:
                return True
        return False
    
    def get_last_activation(self) -> int:
        return self._last_activation