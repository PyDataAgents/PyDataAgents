from dataclasses import dataclass, field
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.buffers.TimedBuffer import TimedBuffer
from pydag.buffers.signals.SampledSignal import SampledSignal
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode


@dataclass
class SampledSignalAction(BufferNode, Action):
    
    signal : SampledSignal = field(default=None, metadata={})
    
    def _on_install(self, agent : Agent = None):
        if self._buffer is None:
            self._buffer = TimedBuffer(capacity=self.n, data_type=DataType.FLOAT.value)
            if agent is not None:
                agent.add_buffer(self._buffer)
        super()._on_install(agent)
       
    def _on_execute(self):
        ts, values = self.signal.samples(self.n)
        if isinstance(self._buffer, TimedBuffer):
            self._buffer.push_timestamps(values, ts)