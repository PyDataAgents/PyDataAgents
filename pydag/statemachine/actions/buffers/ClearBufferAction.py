from ....buffers.Buffer import Buffer
from ....statemachine.Action import Action
from ....statemachine.BufferNode import BufferNode


class ClearBufferAction(BufferNode, Action):
    
    def execute(self):
        if isinstance(self.buffer, Buffer):
            self.buffer.clear()