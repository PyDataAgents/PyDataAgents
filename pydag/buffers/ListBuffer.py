from __future__ import annotations
import copy
import threading

from .Buffer import Buffer
from ..agents.Agent import Agent

class ListBuffer(Buffer):
    """buffer that stores its values in a capacity limited list
    """

    def __post_init__(self):
        super().__post_init__()        
        self.elements = list()
        self.lock = threading.RLock()

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.initial_values is not None:
            self.elements = self.initial_values
            
    def deinstall(self, agent : Agent = None):
        super().deinstall(agent)
        self.elements = []
           
    def push(self, elements : list):
        with self.lock:
            if isinstance(elements, str):
                self.__push1(elements)
            elif hasattr(elements, "__len__"):
                # check for infinity capacity
                if self.capacity != Buffer.INIFINITY_CAPACITY:
                    too_many =  len(elements) + self.size() - self.capacity
                else:
                    too_many = 0
                if too_many > 0:
                    rest = len(elements) - too_many
                    if rest > 0:
                        self.elements.extend(elements[0:rest])
                    i = 0
                    while i < too_many:
                        self.__push1(elements[rest + i])
                        i = i + 1
                else:
                    self.elements.extend(elements)
            else:
                self.__push1(elements)

    def data(self, n : int = 0, persistent : bool = True) -> list:
        with self.lock:
            if self.size() > 0:
                if n > 0:
                    if n > self.size():
                        ListBuffer.LOGGER.warning("buffer only contains " + str(self.size()) + " elements")
                        n = self.size()
                    d = self.elements[0:n]
                    if not persistent:
                        del self.elements[0:n]
                    return d
                else:
                    # always make a deep copy, otherwise a reference will be maintained
                    d = copy.deepcopy(self.elements)
                    if not persistent:
                        self.elements.clear()
                    return d
            else:
                ListBuffer.LOGGER.warning("buffer is empty")
                return []
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        data = {}
        data[Buffer.VALUES] = self.data(n, persistent)
        d = {}
        d[Buffer.DATA] = data
        d[Buffer.META] = self.config_options()
        return d
                    
    def size(self) -> int:
        return len(self.elements)
        
    def __push1(self, element : any):
        """private function for inserting and removing an object if necessary

        Args:
            object (any): a buffer object / sample
        """
        with self.lock:
            # check for infinity capacity
            if self.capacity != Buffer.INIFINITY_CAPACITY:
                if self.size() == self.capacity:
                    self.elements.pop(0)            
            self.elements.append(element)