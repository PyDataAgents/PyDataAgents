import copy
import time
from loguru import logger

from ..agents.AgentConfig import AgentConfig
from .ListBuffer import ListBuffer


class TimedBuffer(ListBuffer):
    """
    A buffer that stores data with timestamps.
    Inherits from ListBuffer.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.timestamps = []  # List to store timestamps corresponding to the data
   
    def push(self, elements : list):
        with self.lock:
            if isinstance(elements, str):
                ts = round(time.time() * 1000)  # Current timestamp in milliseconds
                self.__push_timestamp(elements, ts)
            if hasattr(elements, "__len__"):
                # check for infinity capacity
                if self.capacity != AgentConfig.INFINITE_CAPACITY:
                    too_many =  len(elements) + self.size() - self.capacity
                else:
                    too_many = 0
                if too_many > 0:
                    rest = len(elements) - too_many
                    if rest > 0:
                        self.elements.extend(elements[0:rest])
                        self.timestamps.extend([round(time.time() * 1000)] * rest)
                    i = 0
                    while i < too_many:
                        ts = round(time.time() * 1000)  # Current timestamp in milliseconds
                        self.__push_timestamp(elements[rest + i], ts)
                        i = i + 1
                else:
                    self.elements.extend(elements)
                    self.timestamps.extend([round(time.time() * 1000)] * len(elements))
            else:
                ts = round(time.time() * 1000)  # Current timestamp in milliseconds
                self.__push_timestamp(elements, ts)
    
    def push_timestamps(self, elements : list, timestamps : list):
        with self.lock:
            if isinstance(elements, str):
                self.__push_timestamp(elements, timestamps)
                
            if hasattr(elements, "__len__"):
                # check for infinity capacity
                if self.capacity != AgentConfig.INFINITE_CAPACITY:
                    too_many =  len(elements) + self.size() - self.capacity
                else:
                    too_many = 0
                if too_many > 0:
                    rest = len(elements) - too_many
                    if rest > 0:
                        self.elements.extend(elements[0:rest])
                        self.timestamps.extend(timestamps[0:rest])
                    i = 0
                    while i < too_many:
                        self.__push_timestamp(elements[rest + i], timestamps[rest + i])
                        i = i + 1
                else:
                    self.elements.extend(elements)
                    self.timestamps.extend(timestamps)
            else:
                self.__push_timestamp(elements, timestamps)
                
    def data(self, n : int = 0, persistent : bool = True) -> dict[str, list]:
        with self.lock:
            if self.size() > 0:
                if n > 0:
                    if n > self.size():
                        logger.warning("buffer only contains " + str(self.size()) + " elements")
                        n = self.size()
                    v = self.elements[-n:]
                    t = self.timestamps[-n:]
                    if not persistent:
                        del self.elements[-n:]
                        del self.timestamps[-n:]
                    d = {"values": v, "timestamps": t}
                    return d
                else:
                    # always make a deep copy, otherwise a reference will be maintained
                    v = copy.deepcopy(self.elements)
                    t = copy.deepcopy(self.timestamps)
                    d = {"values": v, "timestamps": t}
                    if not persistent:
                        self.elements.clear()
                        self.timestamps.clear()
                    return d
            else:
                logger.warning("buffer is empty")
                return {}
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d
                
    def __push_timestamp(self, element : any, timestamp : int):
        """private function for inserting a timestamp

        Args:
            element (any): a buffer object / sample
            timestamp (int): the timestamp of the element
        """
        with self.lock:
            # check for infinity capacity
            if self.capacity != AgentConfig.INFINITE_CAPACITY:
                if self.size() == self.capacity:
                    self.timestamps.pop(0)
                    self.elements.pop(0)
                
            self.elements.append(element)
            self.timestamps.append(timestamp)