from __future__ import annotations
import copy
import threading
from typing import Union

from ..agents.AgentConfig import AgentConfig
from .Buffer import Buffer
from ..agents import Agent
import numpy as np

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
    
    def push(self, elements: list | dict):
        
        def _flatten_dict(d: dict, parent_key=""):
            """Recursively flatten dict with dot-separated keys."""
            flat = {}
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    flat.update(_flatten_dict(v, new_key))
                else:
                    flat[new_key] = v
            return flat

        with self.lock:
            if isinstance(elements, dict):
                flat_elements = _flatten_dict(elements)
                for k, v in flat_elements.items():
                    if k not in self.elements or not isinstance(self.elements[k], list):
                        self.elements[k] = []
                    if isinstance(v, list):
                        self.elements[k].extend(v)
                    else:
                        self.elements[k].append(v)

                    # enforce capacity
                    if self.capacity != Buffer.INFINITE_CAPACITY:
                        while len(self.elements[k]) > self.capacity:
                            self.elements[k].pop(0)

            elif isinstance(elements, list) and all(isinstance(el, dict) for el in elements):
                for el in elements:
                    self.push(el)
        

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:
            d = dict()
            for k in self.elements.keys():
                if len(self.elements[k]) < n:
                    n = len(self.elements[k])
                d[k] = self.elements[k][-n:]
                if not persistent:
                    del self.elements[k][-n:]
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
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d

    def size(self) -> int:
        if len(self.elements) == 0:
            return 0
        else:
            return len(next(iter(self.elements.values())))