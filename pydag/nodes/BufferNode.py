from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from loguru import logger

from ..utils.DataUtils import DataUtils
from ..utils.NodeUtils import NodeUtils
from ..nodes.NodeException import NodeException
from ..agents.AgentConfig import AgentConfig
from ..buffers.DictBuffer import DictBuffer
from ..buffers.Buffer import Buffer
from .Node import Node

if TYPE_CHECKING:
    from ..agents.Agent import Agent

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "unique ID of the buffer"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether data is removed (False) from parent or not (True)"})
    n : int = field(default=0, metadata={"description": "specifies how much data is retrieved from parent buffer. Default 0 -> all data"})
    input_keys : list[str] = field(default_factory=list, metadata={"description": "list of input key selectors used to extract data from parent buffers. Each selector can be an exact key name (e.g. 'temperature'), a Python-style slice string over the ordered parent keys (e.g. '1:3' or '0:5:2', stop exclusive), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Multiple selectors are combined with OR semantics, duplicates are removed while preserving first-match order. If empty, all parent keys are returned"})        
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming"})
    ignore_keys : list[str] = field(default_factory=list, metadata={"description": "list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys"})        
    ignore_empty_parents : bool = field(default=True, metadata={"description": "if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True)"})
         
    def __post_init__(self):
        super().__post_init__()
        self._buffer : Buffer = None  # private property for the linked buffer instance

    def _on_install(self, agent : 'Agent' = None):
        """this `install` method connects a `Buffer` instance from specified `agent` based on given `buffer_id`

        Args:
            agent (agent, optional): agent instance. Defaults to None.

        Raises:
            StatemachineException: throws an `Exception` if no `buffer` with the specified `buffer_id` can be found in `agent`
        """
        # check buffer installation
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
                        agent.add_buffer(self._buffer)
                else:
                    self._buffer = DictBuffer(
                                                id=self.id + "-BUFFER",
                                                capacity=AgentConfig.INFINITE_CAPACITY,
                                                timestamps_enabled=True,
                                                index_enabled=True
                                            )
                    self.buffer_id = self._buffer.id
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
        NodeUtils.validate_key_names("input_keys", self.input_keys, allow_special=True)
        NodeUtils.validate_key_names("output_keys", self.output_keys)
        
    def _on_uninstall(self, agent : 'Agent' = None):
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
        
    def get_parent_data(self, by_rows : bool = False) -> dict | list:
        """ Retrieve data from parent node buffers.
        This method aggregates data from one or more parent BufferNode instances.
        For a single parent, it retrieves data directly from that parent's buffer.
        For multiple parents, it merges data from all parents, extending list values
        where keys overlap across parents.
        Parameters
        
        Args:
            by_rows(bool): specifies whether data is retrieved by rows (True) or as columns (False)
            
        Returns:
            dict: A dictionary containing the aggregated data from parent buffers.
            - If input_keys are specified, only those keys are included.
            - If ignore_keys are specified, those keys are excluded from the result.
            - For multiple parents, values are converted to lists and extended
              when the same key exists in multiple parents.
        Raises:
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
                        data = NodeUtils.filter_data_by_selectors(d, self.input_keys)
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
                                    filtered = NodeUtils.filter_data_by_selectors(d, self.input_keys)
                                    for dk, dv in filtered.items():
                                        values = dv if isinstance(dv, list) else [dv]
                                        if dk in data:
                                            data[dk].extend(values)
                                        else:
                                            data[dk] = values
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
        if by_rows:
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
