from dataclasses import dataclass
from ..BufferNode import BufferNode
from ..Transition import Transition


@dataclass
class BufferNotEmptyTransition(BufferNode, Transition):
    """
    A transition that checks if specified buffer is not empty.
    If the buffer is not empty, the transition is successful.
    """
    
    def _on_check(self) -> bool:
        if self._buffer.size() > 0:
            return True
        else:
            return False