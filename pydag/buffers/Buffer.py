from __future__ import annotations
from dataclasses import dataclass, field
import copy
import json
from abc import abstractmethod
import threading
import time
from typing import TYPE_CHECKING, Union


from ..agents.AgentConfig import AgentConfig
from ..agents.AgentStates import AgentElementState, BufferState
from ..utils.ClassUtils import ClassUtils
from .DataType import DataType
from ..agents.AgentElement import AgentElement

if TYPE_CHECKING:
    from ..agents.Agent import Agent

@dataclass
class Buffer(AgentElement):
    """
    Abstract base class for buffers.
    """    
    
    capacity : int = field(default=AgentConfig.INFINITE_CAPACITY, metadata={"description": "Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer."})
    data_type : str = field(default=DataType.FLOAT.value, metadata={"description": "datatype to expect from buffer elements, can be DataType enum or list of enums"})
    initial_values : any = field(default=None, metadata={"description": "initial values in buffer"})
    unit : any = field(default=None, metadata={"description": "unit of element values in this buffer, can be string or list of strings"})
    description : str = field(default=None, metadata={"description": "buffer description"})
    duplicate_ids : list = field(default_factory = list, metadata={"description": "id's of the other buffers used for duplicating the data"})
    
    def __post_init__(self):
        super().__post_init__()
        self._elements = list | dict
        self._duplicates : dict[str, Buffer] = {}
        self._lock = threading.RLock()
        self._state : Union[BufferState, AgentElementState] = AgentElementState.UNINSTALLED
        self._last_timestamp : int = 0
        self._last_timer :int = 0

    def _on_install(self, agent: Agent = None):
        if self.initial_values is not None:
            self._elements = self.initial_values
        if len(self._duplicates) > 0:
            self.duplicate_ids = list(self._duplicates.keys())
        elif len(self.duplicate_ids) > 0:
            for di in self.duplicate_ids:
                if agent is None:
                    buf = ClassUtils.create_instance(self.type)
                    ClassUtils.set_properties(buf, self.config_options())
                    if isinstance(buf, Buffer):
                        buf.id = di
                        buf.duplicate_ids = []
                        buf.install()
                        self._duplicates[buf.id] = buf
                else:
                    if agent.get_buffer(di):
                        self._duplicates[di] = agent.get_buffer(di)
                    else:
                        buf = ClassUtils.create_instance(self.type)
                        ClassUtils.set_properties(buf, self.config_options())
                        if isinstance(buf, Buffer):
                            buf.id = di
                            # clean the duplicate_ids, so that we don't get infinite recursion
                            buf.duplicate_ids = []
                            buf.install(agent)
                            self._duplicates[buf.id] = buf
                            agent.add_buffer(buf)
    
    def _on_uninstall(self, agent : Agent = None):
        if isinstance(self._elements, list):
            self._elements = []
        elif isinstance(self._elements, dict):
            self._elements = {}
        for buf in self._duplicates.values():
            buf.uninstall(agent)
    
    def push(self, elements):
        """
        push new elements to buffer (and to duplicates)
        """
        with self._lock:
            self._state = BufferState.STORING
            self._on_push(elements)
            for dup in self._duplicates.values():
                dup.push(elements)
            self._state = BufferState.IDLE
    
    @abstractmethod  
    def _on_push(self, elements):
        """
        push new elements to buffer
        """

    def data(self, n=0, persistent=True) -> dict:
        """
        get the buffers data, or n samples, with persistent True/False you specify whether to keep the elements in buffer
        the return type should always be a dictionary
        """
        self._state = BufferState.RETRIEVING
        d = self._on_data(n, persistent)
        self._state = BufferState.IDLE
        return d
        
    @abstractmethod
    def _on_data(self, n=0, persistent=True) -> dict:
        """
        retieval logic for the buffers data, or n samples, with persistent True/False you specify whether to keep the elements in buffer
        the return type should always be a dictionary
        """
        

    def clear(self):
        """
        clears all samples from buffer    
        """
        with self._lock:
            self._state = BufferState.RETRIEVING
            self._elements.clear()
            for dup in self._duplicates.values():
                dup._state = BufferState.RETRIEVING
                dup.clear()
                dup._state = BufferState.IDLE
            self._state = BufferState.IDLE

    @abstractmethod
    def size(self) -> int:
        """returns the size of the buffer

        Returns:
            int: number of samples
        """

    @abstractmethod
    def data_with_meta(self, n : int = 0, persistent : bool = True) -> dict:
        pass

    def json(self, n=None, persistent=True):
        # normalize None to 0 samples (i.e., all data) for concrete buffer implementations
        if n is None:
            n = 0
        return json.dumps(self.data_with_meta(n, persistent), ensure_ascii=False)
    
    def to_dict(self) -> dict:
        """ inserts this `Buffer` into a dictionary

        Returns:
            dict: dictionary with this `Buffer` inside
        """
        d = {}
        d[self.id] = self
        return d

    def __str__(self):
        """string representation

        Returns:
            str: string represenation as json
        """
        return self.json(n = 0, persistent=True)  

    def get_duplicates(self) -> dict[str, Buffer]:
        return self._duplicates
    
    def get_last_access(self) -> int:
        """ returns the last access time of the `Buffer` in nanoseconds since epoch

        Returns:
            int: UTC timestamp in ns
        """
        return self._last_timestamp

    def snapshot_state(self) -> dict:
        payload = super().snapshot_state()
        payload.update(
            {
                "elements": copy.deepcopy(self._elements),
                "last_timestamp": self._last_timestamp,
                "last_timer": self._last_timer,
            }
        )
        return payload

    def restore_state(self, payload: dict | None):
        super().restore_state(payload)
        if payload is None:
            return
        self._elements = copy.deepcopy(payload.get("elements", self._elements))
        self._last_timestamp = payload.get("last_timestamp", 0)
        self._last_timer = payload.get("last_timer", 0)
        
        
