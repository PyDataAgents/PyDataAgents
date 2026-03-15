from __future__ import annotations
from dataclasses import dataclass, field
import time
import uuid
from typing import Union


from ..agents.AgentStates import AgentElementState, NodeState
from ..agents.RuntimeStorage import ArtifactPolicy
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
        self._last_timestamp : int = 0
        self._execution_id : str = None
        self._last_transition_timestamp : int = 0
        self._retry_marker : int = 0
        self._interrupted : bool = False
      
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
    
    def get_last_timestamp(self) -> int:
        return self._last_timestamp

    def begin_execution(self):
        self._execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        self._interrupted = False
        self._state = NodeState.EXECUTING

    def end_execution(self):
        self._state = NodeState.IDLE
        self._last_timestamp = time.time_ns()

    def mark_interrupted(self):
        self._interrupted = True

    def mark_retry(self):
        self._retry_marker += 1

    def mark_transition(self):
        self._last_transition_timestamp = time.time_ns()

    def record_output_artifact(self, path: str, name: str = None, managed: bool = False):
        artifact_name = name or f"{self.__class__.__name__}-output"
        self.register_artifact(
            name=artifact_name,
            path=path,
            kind="output_file",
            policy=ArtifactPolicy.DURABLE.value,
            managed=managed,
            metadata={"node_id": self.id, "execution_id": self._execution_id},
        )

    def snapshot_state(self) -> dict:
        payload = super().snapshot_state()
        payload.update(
            {
                "is_active": self._is_active,
                "last_timestamp": self._last_timestamp,
                "execution_id": self._execution_id,
                "last_transition_timestamp": self._last_transition_timestamp,
                "retry_marker": self._retry_marker,
                "interrupted": self._interrupted,
            }
        )
        return payload

    def restore_state(self, payload: dict | None):
        super().restore_state(payload)
        if payload is None:
            return
        self._is_active = payload.get("is_active", True)
        self._last_timestamp = payload.get("last_timestamp", 0)
        self._execution_id = payload.get("execution_id")
        self._last_transition_timestamp = payload.get("last_transition_timestamp", 0)
        self._retry_marker = payload.get("retry_marker", 0)
        self._interrupted = payload.get("interrupted", False)
