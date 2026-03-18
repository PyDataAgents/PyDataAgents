from __future__ import annotations
from dataclasses import dataclass, field
import time
import uuid


from ..agents.AgentStates import NodeState
from ..agents.RuntimeStorage import ArtifactPolicy, stable_fingerprint
from ..agents.AgentElement import AgentElement, persisted_field, runtime_handle_field

@dataclass
class Node(AgentElement):
    child_ids : list[str] = field(default_factory=list, metadata={"description" : "List of child node IDs"})
    _parents : list["Node"] = runtime_handle_field(default_factory=list, init=False, repr=False)
    _children : list["Node"] = runtime_handle_field(default_factory=list, init=False, repr=False)
    _is_active : bool = persisted_field(default=True, init=False, repr=False)
    _last_timestamp : int = persisted_field(default=0, init=False, repr=False)
    _execution_id : str = persisted_field(default=None, init=False, repr=False)
    _last_transition_timestamp : int = persisted_field(default=0, init=False, repr=False)
    _retry_marker : int = persisted_field(default=0, init=False, repr=False)
    _interrupted : bool = persisted_field(default=False, init=False, repr=False)
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

    def get_topology_fingerprint(self, agent=None) -> str | None:
        payload = {
            "parents": sorted([parent.uid for parent in self._parents]),
            "children": sorted([child.uid for child in self._children]),
            "child_ids": sorted(self.child_ids),
        }
        return stable_fingerprint(payload)

    def _default_uid_prefix(self) -> str:
        return "node"
