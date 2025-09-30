from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class MergeBufferAction(BufferNode, Action):
    
    merge_keys : list[str] = field(default_factory=list[str], metadata={"description": "specifies the keys to use from parent buffer(s) for merging, if left empty all parent buffer keys are merged"})
        
    def execute(self):
        # TODO
        pass