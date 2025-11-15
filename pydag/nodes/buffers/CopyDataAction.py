from dataclasses import dataclass

from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class CopyDataAction(BufferNode, Action):
    """ `Action` that makes a copy of the `Buffer` found in the first `BufferNode` found amongst this `Node`s parents.
        If this `Node`'s parents contian more than one `BufferNode`, only the first is respected.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.parent_ref : BufferNode = None
    
    def install(self, agent : Agent = None):
        BufferNode.install(self, agent)
        # check parents for first BufferNode and reference the parent
        for parent in self.parents:
            if isinstance(parent, BufferNode):
                self.parent_ref = parent                    
                break

    def execute(self):
        data = self.parent_ref.buffer.data(n=self.n, persistent=self.persistent)
        self.buffer.push(data)