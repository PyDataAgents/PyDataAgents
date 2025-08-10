from __future__ import annotations
import copy
import threading
from typing import Union

from .Buffer import Buffer
from ..agents import Agent

class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    """
        
    def __post_init__(self):
        super().__post_init__()
        self.elements : dict[list] = dict()
        self.lock = threading.RLock()

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.initial_values is not None:
            self.elements = self.initial_values
        
    def deinstall(self, agent : Agent = None):
        super().deinstall(agent)
        self.elements = {}        
    
    def push(self, elements : Union[list, dict]):
        with self.lock:
            if isinstance(elements, dict):
                for k in elements:
                    if k in self.elements.keys():
                        if isinstance(elements[k], list):
                            self.elements[k].extend(elements[k])
                        else:
                            self.elements[k].append(elements[k])
                        # check for infinity capacity
                        if self.capacity != Buffer.INFINITE_CAPACITY:                            
                            if len(self.elements[k]) > self.capacity:
                                self.elements[k].pop(0)                        
                    else:
                        self.elements[k] = list()
                        if isinstance(elements[k], list):
                            self.elements[k].extend(elements[k])
                        else:
                            self.elements[k].append(elements[k])                        
            elif isinstance(elements, list) and all(isinstance(element, dict) for element in elements):
                for element in elements:
                    self.push(element)
        

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:
            d = dict()
            for k in self.elements.keys():
                if len(self.elements[k]) < n:
                    n = len(self.elements[k])
                d[k] = self.elements[k][0:n]
                if not persistent:
                    del self.elements[k][0:n]
            return d
        else:
            # always make a deep copy, otherwise a reference will be maintained
            d = copy.deepcopy(self.elements)
            if not persistent:
                for k in self.elements.keys():
                    self.elements[k].clear()
            return d
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[Buffer.DATA] = self.data(n, persistent)
        d[Buffer.META] = self.config_options()
        return d

    def size(self) -> int:
        if len(self.elements) == 0:
            return 0
        else:
            return len(next(iter(self.elements.values())))