import copy
from dataclasses import dataclass


from ...buffers.Buffer import Buffer
from ...buffers.TimedBuffer import TimedBuffer
from ...utils.ClassUtils import ClassUtils
from ...agents.Agent import Agent
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode


@dataclass
class CopyBufferAction(BufferNode, Action):
    """ `Action` that copies the entire parent buffer to this `Node`'s `Buffer` whenever executed.
    The copy procedure makes a deep of all the parent's `Buffer` elements
    """
    
    def __post_init__(self):
        super().__post_init__()
        self._parent_ref : BufferNode = None
    
    def _on_install(self, agent : Agent = None):
        # check parents for first BufferNode and reference the parent
        for parent in self._parents:
            if isinstance(parent, BufferNode):
                self._parent_ref = parent
                btype = parent.get_buffer().type
                buf : Buffer = ClassUtils.create_instance(btype)
                ClassUtils.set_properties(buf, parent.get_buffer().config_options())
                if self.buffer_id is not None:
                    buf.id = self.buffer_id
                self._buffer = buf
                if agent is not None:
                    agent.add_buffer(self._buffer)
                self._buffer.install(agent)
                break
    
    def _on_execute(self):
        self._buffer._elements = copy.deepcopy(self._parent_ref.get_buffer()._elements)
        if isinstance(self._buffer, TimedBuffer) and isinstance(self._parent_ref.get_buffer(), TimedBuffer):
            self._buffer._timestamps = copy.deepcopy(self._parent_ref.get_buffer()._timestamps)
                
    