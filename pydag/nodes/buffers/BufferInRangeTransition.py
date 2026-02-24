from dataclasses import dataclass, field
from ...buffers.Comparator import Comparator
from ..BufferNode import BufferNode
from ..Transition import Transition


@dataclass
class BufferInRangeTransition(BufferNode, Transition):
    """
    A transition that compares the current buffer with a target value.
    If the buffer matches the target, the transition is successful.
    """
    
    comparator : str = field(default=None, metadata={"description": "the comparison operator to use"})
    upper_limit : any = field(default=None, metadata={"description": "the upper limit of the range"})
    lower_limit : any = field(default=None, metadata={"description": "the lower limit of the range"})

    def _on_check(self):
        data = self._buffer.data(1, True)
    
        # TODO
        