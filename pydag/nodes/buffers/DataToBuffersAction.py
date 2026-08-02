from dataclasses import dataclass, field

from ...nodes.Node import Node
from ...agents.AgentKeywords import AgentKeywords
from ...nodes.NodeException import NodeException
from ...buffers.DictBuffer import DictBuffer
from ...buffers.Buffer import Buffer
from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class DataToBuffersAction(BufferNode, Action):
    """ `Action` that copies data of the `Buffer` specified via `buffer_id` or found in the first `BufferNode` found amongst this `Node`s parents to all the buffers specified via `buffer_ids`.
        If this `Node`'s parents contain more than one `BufferNode`, only the first is respected.
    """
    
    clear_first : bool = field(default=True, metadata={"description": "if set to true, this Buffer's content is cleared before copying"})
    buffer_ids : list[str] = field(default_factory=list, metadata={"description": "ids of the buffers to copy data to"})
    
    def __post_init__(self):
        super().__post_init__()
        self._buffers : dict[str, Buffer] = None
    
    def _on_install(self, agent : Agent = None):
        if self._buffer is None:
            if self.buffer_id is not None:
                if agent.get_buffer(self.buffer_id):
                    self._buffer = agent.get_buffer(self.buffer_id)
        if self._buffers is not None:
            if agent is not None:
                for buffer in self._buffers.values():
                    if agent.get_buffer(self.buffer_id):
                        buffer.install(agent)
                        agent.add_buffer(buffer)
        else:
            self._buffers = {}
            if agent is not None:
                for buffer_id in self.buffer_ids:
                    if agent.get_buffer(buffer_id):
                        self._buffers[buffer_id] = agent.get_buffer(buffer_id)
                    else:
                        buffer = DictBuffer(id=buffer_id, capacity=AgentKeywords.INFINITE_CAPACITY)
                        buffer.install(agent)
                        agent.add_buffer(buffer)
                        self._buffers[buffer_id] = buffer
            else:
                for buffer_id in self.buffer_ids:
                    buffer = DictBuffer(id=buffer_id, capacity=AgentKeywords.INFINITE_CAPACITY)
                    buffer.install(agent)
                    self._buffers[buffer_id] = buffer
            

    def _on_execute(self):
        if self._buffers is not None:
            data = None
            if self._buffer is None:
                data = self.get_parent_data()
            elif self._buffer is not None:
                data = self._buffer.data(n=self.n, persistent=self.persistent)
            if data is not None:
                for buffer in self._buffers.values():
                    if self.clear_first:
                        buffer.clear()
                    buffer.push(data)
            else:
                raise NodeException(f"No data was extracted from this {Node.cname()}'s {Buffer.cname()} or any parent")
        else:
            raise NodeException("No receiving buffers have been specififed")
        
    def get_buffers(self) -> dict[str, Buffer]:
        return self._buffers
            