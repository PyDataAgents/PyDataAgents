import copy
from dataclasses import dataclass

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
        self.parent_ref : BufferNode = None
    
    def install(self, agent : Agent = None):
        # check parents for first BufferNode and reference the parent
        for parent in self.parents:
            if isinstance(parent, BufferNode):
                self.parent_ref = parent
                btype = parent.buffer.type
                buf = ClassUtils.create_instance(btype)
                ClassUtils.set_properties(buf, parent.buffer.config_options())
                if self.buffer_id is not None:
                    buf.id = self.buffer_id
                self.set_buffer(buf)
                if agent is not None:
                    agent.add_buffer(self.buffer)
                break
    
    def execute(self):
        self.buffer.elements = copy.deepcopy(self.parent_ref.buffer.elements)
        if isinstance(self.buffer, TimedBuffer) and isinstance(self.parent_ref.buffer, TimedBuffer):
            self.buffer.timestamps = copy.deepcopy(self.parent_ref.buffer.timestamps)
                
    