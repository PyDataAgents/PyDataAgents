from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class FormatBufferColumnAction(BufferNode, Action):
    
    create_new : bool = field(default=True, metadata={"description": "specifies whether to create a new Buffer or append the referenced one"})
    format_keys : list[str] = field(default_factory=list[str], metadata={"description": "specifies the keys to use from original buffer(s) to format new column"})
    new_key : str = field(default=None, metadata={"description": "specifies the new column key for the formatted data"})
    format_pattern : str = field(default=None, metadata={"description": "specifies the format pattern for the new column"})
    
    def install(self, agent : Agent = None):
        # TODO here must be decided whether the parents and properties match
        # only one BufferNode parent can be used if create_new = False, and so on
        pass
    
    def execute(self):
        # TODO
        pass