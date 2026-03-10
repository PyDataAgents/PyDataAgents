from dataclasses import dataclass, field
from loguru import logger


from ..utils.DataUtils import DataUtils
from ..nodes.NodeException import NodeException
from ..agents.AgentConfig import AgentConfig
from ..buffers.DictBuffer import DictBuffer
from ..buffers.Buffer import Buffer
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "unique ID of the buffer"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether data is removed (False) from parent or not (True)"})
    n : int = field(default=0, metadata={"description": "specifies how much data is retrieved from parent buffer. Default 0 -> all data"})
    input_keys : list[str] = field(default_factory=list, metadata={"description": "list of keys to extract from parent buffers, defaults to empty and all the keys are returned"})        
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})
    ignore_keys : list[str] = field(default_factory=list, metadata={"description": "list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys"})        
    by_rows : bool = field(default=False, metadata={"description": "specifies whether data is retrieved by rows (True) or as columns (False)"})
    ignore_empty_parents : bool = field(default=True, metadata={"description": "if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True)"})
         
    def __post_init__(self):
        super().__post_init__()
        self._buffer : Buffer = None  # private property for the linked buffer instance

    def _on_install(self, agent : Agent = None):
        """this `install` method connects a `Buffer` instance from specified `agent` based on given `buffer_id`

        Args:
            agent (agent, optional): agent instance. Defaults to None.

        Raises:
            StatemachineException: throws an `Exception` if no `buffer` with the specified `buffer_id` can be found in `agent`
        """
        if self._buffer is None:
            if agent is not None:
                if self.buffer_id is not None:
                    if agent.get_buffer(self.buffer_id):
                        self._buffer = agent.get_buffer(self.buffer_id)
                    else:
                        self._buffer = DictBuffer(
                                                    id=self.buffer_id,
                                                    capacity=AgentConfig.INFINITE_CAPACITY,
                                                    timestamps_enabled=True,
                                                    index_enabled=True
                                                )
                        self._buffer.install(agent)
                        agent.add_buffer(self._buffer)
                else:
                    self._buffer = DictBuffer(
                                                id=self.id + "-BUFFER",
                                                capacity=AgentConfig.INFINITE_CAPACITY,
                                                timestamps_enabled=True,
                                                index_enabled=True
                                            )
                    self.buffer_id = self._buffer.id
                    self._buffer.install(agent)
                    agent.add_buffer(self._buffer)
            else:
                self._buffer = DictBuffer(
                    id=self.id + "-BUFFER",
                    capacity=AgentConfig.INFINITE_CAPACITY,
                    timestamps_enabled=True,
                    index_enabled=True
                )
                self.buffer_id = self._buffer.id
                self._buffer.install(agent)
        
    def _on_uninstall(self, agent : Agent = None):
        self._buffer : Buffer = None
        
    def set_buffer(self, buffer : Buffer):
        """
        method to set the buffer and the `Node`'s `buffer_id`
        <br>this method should always be used in script based `Agent` creation instead of directly assigning a `Buffer` to a `Node`
        <br>>>node.buffer = buffer # DON'T DO 
        <br>>>node.set_buffer(buffer) # DO 
        Args:
            buffer (Buffer): `Buffer` instance
        """
        self._buffer = buffer
        self.buffer_id = buffer.id
    
    def get_buffer(self) -> Buffer:
        """
        method to get the buffer instance
        Returns:
            Buffer: `Buffer` instance
        """
        return self._buffer
        
    def get_parent_data(self) -> dict:
        """Retrieve data from parent node buffers.
        This method aggregates data from one or more parent BufferNode instances.
        For a single parent, it retrieves data directly from that parent's buffer.
        For multiple parents, it merges data from all parents, extending list values
        where keys overlap across parents.
        Parameters
        -------
        dict
            A dictionary containing the aggregated data from parent buffers.
            - If input_keys are specified, only those keys are included.
            - If ignore_keys are specified, those keys are excluded from the result.
            - For multiple parents, values are converted to lists and extended
              when the same key exists in multiple parents.
        Raises
        ------
        NodeException
            If parent is not a BufferNode instance.
            If input_keys are specified but none are found in parent buffer data.
        Notes
        -----
        - Single parent: Returns filtered/unfiltered data based on input_keys
        - Multiple parents: Merges data, converting scalars to lists and extending
          list values for duplicate keys across parents
        - ignore_keys are removed from the final result regardless of source
        """
        data = {}
        if len(self._parents) > 0:
            if len(self._parents) == 1:
                parent = next(iter(self._parents))
                if isinstance(parent, BufferNode):
                    if parent.get_buffer() is None:
                        raise NodeException(f"{Buffer.__name__} not initialized in parent {parent.id}")                        
                    d = parent.get_buffer().data(n = self.n, persistent = self.persistent)
                    if len(self.input_keys) > 0 and d is not None:
                        for dk in self.input_keys:
                            if dk in d:
                                data[dk] = d[dk]
                        if len(data) == 0 and len(d) > 0:
                            if not self.ignore_empty_parents:
                                raise NodeException("None of the specified input_keys were found in the parent buffer data")
                    else:
                        if d:
                            data = d
                        else:
                            if not self.ignore_empty_parents and len(data) == 0:
                                raise NodeException("No data was found in the parent buffer")
                            else:
                                data = {}
                else:
                    raise NodeException("Parent is not a " + BufferNode.cname())
            else:
                data = {}
                for parent in self._parents:
                    if isinstance(parent, BufferNode):
                        if parent.get_buffer() is None:
                            raise NodeException(f"{Buffer.__name__} not initialized in parent {parent.id}")
                        d = parent.get_buffer().data(n = self.n, persistent = self.persistent)
                        if d is not None:
                            if len(d) > 0:
                                if len(self.input_keys) > 0:
                                    for dk in self.input_keys:
                                        if dk in d:
                                            if dk in data:
                                                data[dk].extend(d[dk])
                                            else:
                                                if isinstance(d[dk], list):
                                                    data[dk] = d[dk]
                                                else:
                                                    data[dk] = [d[dk]] 
                                else:
                                    for key, value in d.items():
                                        if key in data:
                                            data[key].extend(value)
                                        else:
                                            if isinstance(value, list):
                                                data[key] = value
                                            else:
                                                data[key] = [value]
                    else:
                        logger.debug("Parent is not a " + BufferNode.cname())
                if len(data) == 0:
                    if not self.ignore_empty_parents:
                        if len(self.input_keys) > 0:
                            raise NodeException("None of the specified input_keys were found in the parent buffers data")                            
                        else:
                            raise NodeException("No data was found in the parent buffer data")
            for ik in self.ignore_keys:
                if ik in data:
                    del data[ik]
        if self.by_rows:
            data = DataUtils.dict_to_list(data)
        return data
        
    def get_meta_info(self) -> dict:
        """
        Method to get the meta information from the parents' buffer(s).
        """
        if len(self._parents) > 0:
            if len(self._parents) == 1:
                parent = next(iter(self._parents))
                if isinstance(parent, BufferNode):
                    return parent.get_buffer().config_options()
                else:
                    raise NodeException("Parent is not a " + BufferNode.cname())
            else:
                meta = {}
                for parent in self._parents:
                    if isinstance(parent, BufferNode):
                        m = parent.get_buffer().config_options()
                        for key, value in m.items():
                            if key in meta:
                                meta[key].extend(value)
                            else:
                                meta[key] = [value]
                    else:
                        logger.debug("Parent is not a " + BufferNode.cname())
            return meta
        else:
            return {}
        
        
    def add_data(self, data : dict):
        """
        Method to transfers the data to the `BufferNode`'s buffer.
        """
        self._buffer.push(data)
            
    def get_data_size(self) -> int:
        """
        Returns the size of the data in the BufferNode's parent(s) buffer(s).
        
        Returns:
            int: The size of the data.
        """
        if len(self._parents) > 0:
            if len(self._parents) == 1:
                parent = next(iter(self._parents))
                if isinstance(self._parents[0], BufferNode):
                    return self._parents[0].get_buffer().size()
                else:
                    raise NodeException("Parent is not a " + BufferNode.cname())                
            else:
                sizes = []
                for parent in self._parents:
                    if isinstance(parent, BufferNode):
                        sizes.append(parent.get_buffer().size())
                    else:
                        logger.debug("Parent is not a " + BufferNode.cname())
                return max(sizes)
        else:
            return 0
    
    def set_meta_info(self, meta : dict):
        """
        Method to set meta information in the BufferNode's buffer.
        """
        if meta is not None:
            for key in meta:
                if hasattr(self._buffer, key):
                    setattr(self._buffer, key, meta[key]) 
