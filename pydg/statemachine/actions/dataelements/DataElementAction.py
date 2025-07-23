from dataclasses import dataclass, field
from pydg.statemachine.Action import Action
from pydg.statemachine.BufferNode import BufferNode


@dataclass
class DataElementAction(BufferNode, Action):
        
    def __init__(self):
        super().__init__()
           