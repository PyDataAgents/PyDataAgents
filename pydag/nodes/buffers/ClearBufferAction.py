from ...buffers.Buffer import Buffer
from ..Action import Action
from ..BufferNode import BufferNode


class ClearBufferAction(BufferNode, Action):
    
    def _on_execute(self):
        if isinstance(self._buffer, Buffer):
            self._buffer.clear()