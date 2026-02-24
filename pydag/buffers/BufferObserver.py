from dataclasses import dataclass, field
from ..buffers.Buffer import Buffer
from ..services.Observer import Observer


@dataclass
class BufferObserver(Observer):
    
    buffer_id : str = field(default=None, metadata={"description": "id of the buffer to observe"})
    
    def __post_init__(self):
        self._buffer : Buffer = None