from dataclasses import dataclass, field

from ..buffers.BufferObserver import BufferObserver
from ..buffers.ListBuffer import ListBuffer


@dataclass
class ObservedListBuffer(ListBuffer):
    
    input_observers : list[BufferObserver] = field(default_factory=list, metadata={"description" : "list of observers that observe new input to the buffer inside the push method"})
    output_observers : list[BufferObserver] = field(default_factory=list, metadata={"description" : "list of observers that observe output of the buffer inside the data method"})
    
    # TODO