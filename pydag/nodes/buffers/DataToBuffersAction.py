from dataclasses import dataclass, field

from ...nodes.Node import Node
from ...agents.AgentConfig import AgentConfig
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
    
    buffer_ids : list[str] = field(default_factory=list, metadata={"description": "ids of the buffers to copy data to"})
    
    def __post_init__(self):
        super().__post_init__()
        self.parent_ref : BufferNode = None
        self.buffers : dict[str, Buffer] = None
    
    def install(self, agent : Agent = None):
        Action.install(self, agent)
        if self.buffer is None:
            if self.buffer_id is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
        if self.buffer is None:
            # check parents for first BufferNode and reference the parent
            for parent in self.parents:
                if isinstance(parent, BufferNode):
                    self.parent_ref = parent                    
                    break
        if self.buffers is not None:
            if agent is not None:
                for buffer in self.buffers.values():
                    if buffer.id not in agent.buffer_store:
                        buffer.install(agent)
                        agent.add_buffer(buffer)
        else:
            self.buffers = {}
            if agent is not None:
                for buffer_id in self.buffer_ids:
                    if buffer_id in agent.buffer_store:
                        self.buffers[buffer_id] = agent.buffer_store[buffer_id]
                    else:
                        buffer = DictBuffer(id=buffer_id, capacity=AgentConfig.INFINITE_CAPACITY)
                        buffer.install(agent)
                        agent.add_buffer(buffer)
                        self.buffers[buffer_id] = buffer
            else:
                for buffer_id in self.buffer_ids:
                    buffer = DictBuffer(id=buffer_id, capacity=AgentConfig.INFINITE_CAPACITY)
                    buffer.install(agent)
                    self.buffers[buffer_id] = buffer
            

    def execute(self):
        if self.buffers is not None:
            data = None
            if self.buffer is None:
                if self.parent_ref is not None:
                    data = self.parent_ref.buffer.data(n=self.n, persistent=self.persistent)                    
                else:
                    raise NodeException(f"No parent with {Buffer.cname()} was specififed")
            elif self.buffer is not None:
                data = self.buffer.data(n=self.n, persistent=self.persistent)
            if data is not None:
                for buffer in self.buffers.values():
                    buffer.push(data)
            else:
                raise NodeException(f"No data was extracted from this {Node.cname()}'s {Buffer.cname()} or any parent")
        else:
            raise NodeException("No receiving buffers have been specififed")
            