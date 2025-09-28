from ...buffers.Buffer import Buffer
from ..Action import Action
from ..BufferNode import BufferNode


class ClearBufferAction(BufferNode, Action):
    
    def execute(self):
        if isinstance(self.buffer, Buffer):
            self.buffer.clear()