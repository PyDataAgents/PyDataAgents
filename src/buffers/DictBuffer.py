import json
import threading
from PyDataGrabber.src.buffers.Buffer import Buffer, DataType

class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data

    Args:
        Buffer (_type_): _description_
    """

    def __init__(self, id : str = None, capacity : int = 1, data_type : list[DataType] = None, unit : list[str] = None, initial_values: dict = None, description: str = None):
        super().__init__(id=id, capacity=capacity, data_type=data_type, unit=unit, initial_values=initial_values, description=description)
        self.buffer = dict()
        if self.initial_values != None:
            self.buffer = self.initial_values
        self.lock = threading.RLock()

    def push(self, objects : dict):
        with self.lock:
            for k in objects:
                if k in self.buffer.keys():
                    self.buffer[k].append(objects[k])
                    if len(self.buffer[k]) > self.capacity:
                        self.buffer[k].pop(0)
                else:
                    self.buffer[k] = list()
                    self.buffer[k].append(objects[k])
        

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:            
            d = dict()
            for k in self.buffer.keys():
                if len(self.buffer[k]) < n:
                    n = len(self.buffer[k])
                d[k] = self.buffer[k][0:n]
                if not persistent:
                    del self.buffer[k][0:n]
            return d        
        else:
            if persistent:    
                return self.buffer
            else:
                d = self.buffer.copy()
                for k in self.buffer.keys():
                    self.buffer[k].clear()
                return d
        
    def size(self) -> int:
        return len(self.buffer[self.buffer.keys()[0]])