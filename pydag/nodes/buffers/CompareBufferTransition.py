from dataclasses import dataclass, field
from loguru import logger

from ...buffers.Comparator import Comparator
from ..BufferNode import BufferNode
from ..Transition import Transition


@dataclass
class CompareBufferTransition(BufferNode, Transition):
    """
    A transition that compares the current buffer with a target value.
    If the buffer matches the target, the transition is successful.
    """
    
    comparator : str = field(default=None, metadata={"description": "The comparison operator to use."})
    value : any = field(default=None, metadata={"description": "The value to compare against the buffer."})

    def check(self):
        data = self.buffer.data(1, True)
        match self.comparator:
            case Comparator.EQUAL.value:
                return data == self.value
            case Comparator.NOT_EQUAL.value:
                return data != self.value
            case Comparator.EQUAL_OR_GREATER.value:
                return data >= self.value
            case Comparator.GREATER.value:
                return data > self.value
            case Comparator.EQUAL_OR_LESS.value:
                return data <= self.value
            case Comparator.LESS.value:
                return data < self.value
            case Comparator.LIKE.value:
                if isinstance(data, str):
                    if data in self.value:
                        return True
                else:
                    logger.warning(f"Comparator {self.comparator} is not applicable for data type {type(data)}.")                    
                    return False
            case Comparator.NOT_LIKE.value:
                if isinstance(data, str):
                    if data not in self.value:
                        return True
                else:
                    logger.warning(f"Comparator {self.comparator} is not applicable for data type {type(data)}.")                    
                    return False
            case Comparator.NOT_NULL.value:
                if data is not None:
                    return True
                else:
                    return False
            case _:
                logger.error(f"Unknown comparator: {self.comparator}.")
                return False
        