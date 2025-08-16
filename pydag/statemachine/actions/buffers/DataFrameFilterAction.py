from dataclasses import dataclass, field
from pydag.statemachine.Action import Action
from pydag.statemachine.BufferNode import BufferNode


@dataclass
class DataFrameFilterAction(BufferNode, Action):
    
    filter : str = field(default=None, metadata={"description": "pandas filter command to apply to parents' buffer(s)"})