from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING, Any
from loguru import logger

from ..utils.DataUtils import DataUtils
from ..nodes.NodeException import NodeException
from ..agents.AgentKeywords import AgentKeywords
from ..buffers.DictBuffer import DictBuffer
from ..buffers.Buffer import Buffer
from .Node import Node

if TYPE_CHECKING:
    from ..agents.Agent import Agent

TYPE_STRING = "type:string"
TYPE_NUMBER = "type:number"
INDEX_PATTERN = re.compile(r"^\s*-?\d+\s*$")
SLICE_PATTERN = re.compile(r"^\s*(-?\d*)\s*:\s*(-?\d*)\s*(?::\s*(-?\d*)\s*)?$")

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "unique ID of the buffer"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether data is removed (False) from parent or not (True)"})
    n : int = field(default=0, metadata={"description": "specifies how much data is retrieved from parent buffer. Default 0 -> all data"})
    input_keys : list[str] | list[int] | str = field(default_factory=list, metadata={"description": "list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned"})
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
                                                    capacity=AgentKeywords.INFINITE_CAPACITY,
                                                    timestamps_enabled=True,
                                                    index_enabled=True
                                                )
                        agent.add_buffer(self._buffer)
                else:
                    self._buffer = DictBuffer(
                                                id=self.id + "-BUFFER",
                                                capacity=AgentKeywords.INFINITE_CAPACITY,
                                                timestamps_enabled=True,
                                                index_enabled=True
                                            )
                    self.buffer_id = self._buffer.id
                    agent.add_buffer(self._buffer)
            else:
                self._buffer = DictBuffer(
                    id=self.id + "-BUFFER",
                    capacity=AgentKeywords.INFINITE_CAPACITY,
                    timestamps_enabled=True,
                    index_enabled=True
                )
                self.buffer_id = self._buffer.id            
            self._buffer.install(agent)
        BufferNode._validate_keys(self.input_keys)
        BufferNode._validate_keys(self.output_keys)
        
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
        if len(self._parents) > 0:
            data = {}
            has_buffer_parent : bool = False
            for parent in self._parents:
                if isinstance(parent, BufferNode):
                    has_buffer_parent = True
                    if parent.get_buffer() is None:
                        raise NodeException(f"{Buffer.__name__} not initialized in parent {parent.id}")
                    d = parent.get_buffer().data(n = self.n, persistent = self.persistent)
                    if d is not None:
                        if len(d) > 0:
                            if isinstance(self.input_keys, list):
                                if len(self.input_keys) == 0:
                                    for key, values in d.items():
                                        if key in data:
                                            data[key].extend(values)
                                        else:
                                            if isinstance(values, list):
                                                data[key] = values
                                            else:
                                                data[key] = [values]
                                elif isinstance(self.input_keys[0], str):
                                    for ik in self.input_keys:
                                        if ik in d:
                                            values = d[ik]
                                            if ik in data:
                                                data[ik].extend(values)
                                            else:
                                                if isinstance(values, list):
                                                    data[ik] = values
                                                else:
                                                    data[ik] = [values]
                                elif isinstance(self.input_keys[0], int):
                                    i : int = 0
                                    for k, values in d.items():
                                        if i in self.input_keys:
                                            if k in data:
                                                data[k].extend(values)
                                            else:
                                                if isinstance(values, list):
                                                    data[k] = values
                                                else:
                                                    data[k] = [values]
                                        i += 1
                            elif isinstance(self.input_keys, str):
                                selected_keys = BufferNode._parse_keys(list(d.keys()), self.input_keys, d)
                                for k in selected_keys:
                                    if k in d:
                                        values = d[k]
                                        if k in data:
                                            data[k].extend(values)
                                        else:
                                            if isinstance(values, list):
                                                data[k] = values
                                            else:
                                                data[k] = [values]
                else:
                    logger.debug("Parent is not a " + BufferNode.cname())
            
            if not has_buffer_parent:
                raise NodeException(f"No parent {BufferNode.__name__} was specified for this {self.__class__.__name__}, get_parent_data() cannot be executed")
            
            for ik in self.ignore_keys:
                if ik in data:
                    del data[ik]            
            
            if len(data) == 0:
                if not self.ignore_empty_parents:
                    if len(self.input_keys) > 0:
                        raise NodeException("None of the specified input_keys were found in the parent buffers data")                            
                    else:
                        raise NodeException("No data was found in the parent buffer data")
            
            if by_rows:
                data = DataUtils.dict_to_list(data)
            
            return data
        else:
            raise NodeException(f"No parent {Node.__name__} was specified for this {self.__class__.__name__}, get_parent_data() cannot be executed")
        
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
                    
    @staticmethod
    def _validate_keys(keys : list[str] | list[int] | str):
        if keys is None:
            return
        
        if not isinstance(keys, list):
            if not isinstance(keys, str):
                raise NodeException(f"keys must be a list of str | int or a str")

        if isinstance(keys, list):
            if len(keys) > 0:
                if isinstance(keys[0], str):
                    seen = set()
                    for key in keys:
                        if not isinstance(key, str) or key.strip() == "":
                            raise NodeException(f"keys must contain only non-empty strings")
                        normalized = key.strip()
                        if normalized in seen:
                            raise NodeException(f"keys must contain unique entries")
                        seen.add(normalized)
                elif isinstance(keys[0], int):
                    for k in keys:
                        if not isinstance(k, int):
                            raise NodeException("keys must contain all integer entries")
                else:
                    raise NodeException("keys must be either all int or str entries")
            
        elif isinstance(keys, str):
            if keys.startswith("type:"):
                known_type_pattern : bool = False
                if keys == TYPE_STRING:
                    known_type_pattern = True
                elif keys == TYPE_NUMBER:
                    known_type_pattern = True
                if not known_type_pattern:
                    raise NodeException("unknown string pattern for keys was specified")
            return
        
        else:
            raise NodeException("Wrong input type for keys")
        
    @staticmethod
    def _parse_keys(keys : list[str], input_key_pattern : str, data : dict[str, list[Any]]) -> list[str]:
        if input_key_pattern == TYPE_STRING:
            return [key for key in keys if isinstance(BufferNode._sample_value(data[key]), str)]
        if input_key_pattern == TYPE_NUMBER:
            return [ key for key in keys if isinstance(BufferNode._sample_value(data[key]), (int, float, bool))]

        match = SLICE_PATTERN.match(input_key_pattern)
        if match:
            return keys[slice(*(BufferNode._to_int(value) for value in match.groups()))]

        if input_key_pattern in keys:
            return [input_key_pattern]

        if INDEX_PATTERN.match(input_key_pattern):
            index = int(input_key_pattern)
            if -len(keys) <= index < len(keys):
                return [keys[index]]

        return []

    @staticmethod
    def _sample_value(value):
        if isinstance(value, list):
            for item in value:
                if item is not None:
                    return item
            return None
        return value
    
    @staticmethod
    def _to_int(value: str):
        return None if value is None or value == "" else int(value)
