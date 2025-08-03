from dataclasses import dataclass
from ..BufferNode import BufferNode
from ..Transition import Transition


@dataclass
class BufferEmptyTransition(BufferNode, Transition):
    """
    A transition that checks if specified buffer is empty.
    If the buffer is empty, the transition is successful.
    """
    
    def __init__(self):
        super().__init__()
    
    def check(self) -> bool:
        if len(self.buffer) == 0:
            return True
        else:
            return False