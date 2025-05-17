import json
import threading
from PyDataGrabber.src.buffers.Buffer import Buffer, DataType

class ListBuffer(Buffer):
    """buffer that stores its values in a capacity limited list
    """

    def __init__(self, id : str = None, capacity : int = 1, data_type : list[DataType] = None, unit : list[str] = None, initial_values : list = None, description : str = None):
        super().__init__(id = id, capacity = capacity, data_type=data_type, initial_values=initial_values, description=description)        
        if self.initial_values != None:
            self.buffer = self.initial_values
        else:
            self.buffer = list()
        self.lock = threading.RLock()

    def push(self, objects : list):
        with self.lock:
            if hasattr(objects, "__len__"):
                tooMany =  len(objects) + self.size() - self.capacity
                if tooMany > 0:
                    rest = len(objects) - tooMany
                    if rest > 0:
                        self.buffer.extend(objects[0:rest])
                    i = 0
                    while i < tooMany:
                        self.__push1(objects[rest + i])
                        i = i + 1
                else:
                    self.buffer.extend(objects)
            else:
                self.__push1(objects)

    def data(self, n : int = 0, persistent : bool = True) -> list:
        with self.lock:
            if n > 0:
                if n > self.size():
                    ListBuffer.LOGGER.warning("buffer only contains " + self.size() + " objects")
                    n = self.size()
                d = self.buffer[0:n]
                if not persistent:
                    del self.buffer[0:n]
                return d
            else:
                d = self.buffer
                if not persistent:
                    self.buffer.clear
                return d
    
    def size(self) -> int:
        return len(self.buffer)
        
    def __push1(self, object : any):
        """private function for inserting and removing an object if necessary

        Args:
            object (any): a buffer object / sample
        """
        with self.lock:        
            if self.size() == self.capacity:
                self.buffer.pop(0)
            
            self.buffer.append(object)