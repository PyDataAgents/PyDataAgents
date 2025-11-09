from dataclasses import dataclass, field

from ..agents.AgentConfig import AgentConfig
from ..buffers.DictBuffer import DictBuffer
from ..buffers.Buffer import Buffer
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(init=True, default=None, metadata={"description": "unique ID of the buffer"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether data is removed (False) from parent or not (True)"})
    n : int = field(default=0, metadata={"description": "specifies how much data is retrieved from parent buffer. Default 0 -> all data"})
    # New timestamp-related parameters (DictBuffer-specific)
    timestamps_enabled: bool = field(default=False, metadata={"description": "Enable timestamps in underlying DictBuffer."})
    timestamps_key: str = field(default="timestamps", metadata={"description": "Key name for timestamps column."})
    index_enabled : bool = field(default=False, metadata={"description": "Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point."})
    index_key : str = field(default="index", metadata={"description": "Key name for index column."})
    
    def __post_init__(self):
        super().__post_init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance
        
    def install(self, agent : Agent = None):
        """this `install` method connects a `Buffer` instance from specified `agent` based on given `buffer_id`

        Args:
            agent (agent, optional): agent instance. Defaults to None.

        Raises:
            StatemachineException: throws an `Exception` if no `buffer` with the specified `buffer_id` can be found in `agent`
        """
        super().install(agent)
        if self.buffer is None:
            if agent is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
                else:
                    self.buffer = DictBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY,
                                             timestamps_enabled=self.timestamps_enabled,
                                             timestamps_key=self.timestamps_key,
                                             index_enabled=self.index_enabled,
                                             index_key=self.index_key)
                    self.buffer_id = self.buffer.id
                    self.buffer.install(agent)
                    agent.add_buffer(self.buffer)
            else:
                self.buffer = DictBuffer(
                    id=self.id + "-BUFFER",
                    capacity=AgentConfig.INFINITE_CAPACITY,
                    timestamps_enabled=self.timestamps_enabled,
                    timestamps_key=self.timestamps_key,
                    index_enabled=self.index_enabled,
                    index_key=self.index_key
                )
                self.buffer_id = self.buffer.id
                self.buffer.install(agent)
        
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        self.buffer : Buffer = None
        
    def set_buffer(self, buffer : Buffer):
        """
        method to set the buffer and the `Node`'s `buffer_id`
        <br>this method should always be used in script based `Agent` creation instead of directly assigning a `Buffer` to a `Node`
        <br>>>node.buffer = buffer # DON'T DO 
        <br>>>node.set_buffer(buffer) # DO 
        Args:
            buffer (Buffer): `Buffer` instance
        """
        self.buffer = buffer
        self.buffer_id = buffer.id
            