from __future__ import annotations
import copy
import time
from loguru import logger
import numpy as np

from ..agents.AgentKeywords import AgentKeywords
from .Buffer import Buffer

class ListBuffer(Buffer):
    """`Buffer` that stores its values in a capacity limited list
    """

    def __post_init__(self):
        super().__post_init__()        
        self._elements = list()
               
    def _on_push(self, elements : list):
        if isinstance(elements, str):
            self._push1(elements)
        elif isinstance(elements, np.ndarray):
            ## convert to list for serialization
            #li = elements.tolist()
            self._push1(elements)
        elif hasattr(elements, "__len__"):
            if isinstance(elements, dict):
                values = elements.values()
                elements = []
                for value in values:
                    if isinstance(value, list):
                        elements.extend(value)
                    else:
                        elements.append(value)   
                logger.debug("converted dict to list for " + ListBuffer.cname() + " push, "  + ListBuffer.cname() + " only accepts list elements")          
            # check for infinity capacity
            if self.capacity != AgentKeywords.INFINITE_CAPACITY:
                too_many =  len(elements) + self.size() - self.capacity
            else:
                too_many = 0
            if too_many > 0:
                rest = len(elements) - too_many
                if rest > 0:
                    self._elements.extend(elements[0:rest])
                i = 0
                while i < too_many:
                    self._push1(elements[rest + i])
                    i = i + 1
            else:
                self._elements.extend(elements)
        else:
            self._push1(elements)
        self._last_timestamp = time.time_ns()

    def _on_data(self, n : int = 0, persistent : bool = True) -> dict:
        if self.size() > 0:
            if n > 0:
                if n > self.size():
                    logger.warning("buffer only contains " + str(self.size()) + " elements")
                    n = self.size()
                d = self._elements[0:n]
                if not persistent:
                    with self._lock:
                        del self._elements[0:n]
                dic : dict = {}
                dic[AgentKeywords.VALUES] = d
                return dic
            else:
                # always make a deep copy, otherwise a reference will be maintained
                d = copy.deepcopy(self._elements)
                if not persistent:
                    with self._lock:
                        self._elements.clear()
                dic : dict = {}
                dic[AgentKeywords.VALUES] = d
                return dic
        else:
            #logger.warning("buffer is empty")
            return {}

    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        data = {}
        data[AgentKeywords.VALUES] = self.data(n, persistent)
        d = {}
        d[AgentKeywords.DATA] = data
        d[AgentKeywords.META] = self.config_options()
        return d
                    
    def size(self) -> int:
        return len(self._elements)
            
    def _push1(self, element : any):
        """private function for inserting and removing an object if necessary

        Args:
            object (any): a buffer object / sample
        """
        # check for infinity capacity
        if self.capacity != AgentKeywords.INFINITE_CAPACITY:
            if self.size() == self.capacity and self.capacity != 0:
                self._elements.pop(0)  
        self._elements.append(element)