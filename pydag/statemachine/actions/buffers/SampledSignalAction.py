from dataclasses import dataclass, field
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.TimedBuffer import TimedBuffer
from pydag.buffers.signals.SampledSignal import SampledSignal
from pydag.statemachine.Action import Action
from pydag.statemachine.BufferNode import BufferNode


@dataclass
class SampledSignalAction(BufferNode, Action):
    
    signal : SampledSignal = field(default=None, metadata={})
    n : int = field(default=1, metadata={})
    
    def install(self, agent : Agent = None):
        if self.buffer is None:
            self.buffer = TimedBuffer(capacity=self.n, data_type=DataType.FLOAT.value)
            if agent is not None:
                agent.add_buffer(self.buffer)
       
    def execute(self):
        ts, values = self.signal.samples(self.n)
        if isinstance(self.buffer, TimedBuffer):
            self.buffer.push_timestamps(values, ts)