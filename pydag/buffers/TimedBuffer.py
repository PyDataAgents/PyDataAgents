import copy
import time
from loguru import logger

from ..agents.AgentConfig import AgentConfig
from .ListBuffer import ListBuffer


class TimedBuffer(ListBuffer):
    """
    A buffer that stores data with timestamps.
    Inherits from `ListBuffer`.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self._timestamps = []  # List to store timestamps corresponding to the data
   
    def _on_push(self, elements : list):
        if isinstance(elements, str):
            ts = round(time.time() * 1000)  # Current timestamp in milliseconds
            self._push_timestamp(elements, ts)
        elif hasattr(elements, "__len__"):
            # check for infinity capacity
            if self.capacity != AgentConfig.INFINITE_CAPACITY:
                too_many =  len(elements) + self.size() - self.capacity
            else:
                too_many = 0
            if too_many > 0:
                rest = len(elements) - too_many
                if rest > 0:
                    self._elements.extend(elements[0:rest])
                    self._timestamps.extend([round(time.time() * 1000)] * rest)
                i = 0
                while i < too_many:
                    ts = round(time.time() * 1000)  # Current timestamp in milliseconds
                    self._push_timestamp(elements[rest + i], ts)
                    i = i + 1
            else:
                self._elements.extend(elements)
                self._timestamps.extend([round(time.time() * 1000)] * len(elements))
        else:
            ts = round(time.time() * 1000)  # Current timestamp in milliseconds
            self._push_timestamp(elements, ts)
    
    def push_timestamps(self, elements : list, timestamps : list):
        if isinstance(elements, str):
            self._push_timestamp(elements, timestamps)                
        elif hasattr(elements, "__len__"):
            # check for infinity capacity
            if self.capacity != AgentConfig.INFINITE_CAPACITY:
                too_many =  len(elements) + self.size() - self.capacity
            else:
                too_many = 0
            if too_many > 0:
                rest = len(elements) - too_many
                if rest > 0:
                    self._elements.extend(elements[0:rest])
                    self._timestamps.extend(timestamps[0:rest])
                i = 0
                while i < too_many:
                    self._push_timestamp(elements[rest + i], timestamps[rest + i])
                    i = i + 1
            else:
                self._elements.extend(elements)
                self._timestamps.extend(timestamps)
        else:
            self._push_timestamp(elements, timestamps)
        for dup in self._duplicates.values():
            if isinstance(dup, TimedBuffer):
                dup.push_timestamps(elements, timestamps)
                
    def _on_data(self, n : int = 0, persistent : bool = True) -> dict[str, list]:
        if self.size() > 0:
            if n > 0:
                if n > self.size():
                    logger.warning("buffer only contains " + str(self.size()) + " elements")
                    n = self.size()
                v = self._elements[0:n]
                t = self._timestamps[0:n]
                if not persistent:
                    with self._lock:            
                        del self._elements[0:n]
                        del self._timestamps[0:n]
                d = {AgentConfig.TIMESTAMPS: t, AgentConfig.VALUES: v}
                return d
            else:
                # always make a deep copy, otherwise a reference will be maintained
                v = copy.deepcopy(self._elements)
                t = copy.deepcopy(self._timestamps)
                d = {AgentConfig.TIMESTAMPS: t, AgentConfig.VALUES: v}
                if not persistent:
                    with self._lock:
                        self._elements.clear()
                        self._timestamps.clear()
                return d
        else:
            logger.warning("buffer is empty")
            return {}
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d
    
    def clear(self):
        super().clear()
        self._timestamps.clear()
                
    def _push_timestamp(self, element : any, timestamp : int):
        """private function for inserting a timestamp

        Args:
            element (any): a buffer object / sample
            timestamp (int): the timestamp of the element
        """
        # check for infinity capacity
        if self.capacity != AgentConfig.INFINITE_CAPACITY:
            if self.size() == self.capacity:
                self._timestamps.pop(0)
                self._elements.pop(0)
            
        self._elements.append(element)
        self._timestamps.append(timestamp)