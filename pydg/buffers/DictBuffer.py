from __future__ import annotations
import threading
from .Buffer import Buffer
from ..grabbers import Grabber

class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    """
    
    def __init__(self):
        super().__init__()
        self.elements : dict[list] = dict()
        self.lock = threading.RLock()

    def install(self, grabber : Grabber = None):
        super().install(grabber)
        if self.initial_values is not None:
            self.elements = self.initial_values
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.elements = {}        
    
    def push(self, elements : dict):
        with self.lock:
            for k in elements:
                if k in self.elements.keys():
                    self.elements[k].append(elements[k])
                    if len(self.elements[k]) > self.capacity:
                        self.elements[k].pop(0)
                else:
                    self.elements[k] = list()
                    self.elements[k].append(elements[k])
        

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
            if persistent:
                return self.elements
            else:
                d = self.elements.copy()
                for k in self.elements.keys():
                    self.elements[k].clear()
                return d
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d["data"] = self.data(n, persistent)
        d["meta"] = self.config_options()
        return d

    def size(self) -> int:
        return len(self.elements[self.elements.keys()[0]])