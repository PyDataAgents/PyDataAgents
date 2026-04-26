from __future__ import annotations
from dataclasses import dataclass, field
import json
from abc import abstractmethod
import threading
from typing import TYPE_CHECKING, Union


from .BufferException import BufferException
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
            # remove the initial values to keep buffer object small
            self.initial_values = None
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
    
    def _check_state(self, next_state : AgentElementState):
        match(next_state):
            case AgentElementState.UNINSTALLED:
                if self._state != AgentElementState.ERROR and self._state != AgentElementState.INSTALLED:
                    raise BufferException(f"{Buffer.__name__} {self.id} must be installed or has an error before uninstalling!")
                    
            case AgentElementState.INSTALLED:
                # all other states are allowed
                return
            
            case AgentElementState.ERROR:
                # all other states are allowed
                return
            
            case BufferState.STORING:
                if self._state != AgentElementState.INSTALLED:
                    raise BufferException(f"{Buffer.__name__} {self.id} must be installed before storing data!")
                    
            case BufferState.RETRIEVING:
                if self._state == AgentElementState.UNINSTALLED or self._state == AgentElementState.ERROR:
                    raise BufferException(f"{Buffer.__name__} {self.id} must be installed before retrieving data!")
    
    def push(self, elements):
        """
        push new elements to buffer (and to duplicates)
        """
        with self._lock:
            self._check_state(BufferState.STORING)
            self._state = BufferState.STORING
            self._on_push(elements)
            for dup in self._duplicates.values():
                dup.push(elements)
            self._state = BufferState.INSTALLED
    
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
        self._check_state(BufferState.RETRIEVING)
        self._state = BufferState.RETRIEVING
        d = self._on_data(n, persistent)
        self._state = BufferState.INSTALLED
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
                dup.set_state(BufferState.RETRIEVING)
                dup.clear()
                dup.set_state(BufferState.INSTALLED)
            self._state = BufferState.INSTALLED

    @abstractmethod
    def size(self) -> int:
        """returns the size of the buffer

        Returns:
            int: number of samples
        """

    @abstractmethod
    def data_with_meta(self, n : int = 0, persistent : bool = True) -> dict:
        pass

    def save(self):
        # move element values to initial values for being saved
        self.initial_values = self._elements
        super().save()
        # clear after saving to save space
        self.initial_values = None

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
        
        