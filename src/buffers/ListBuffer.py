import threading
from PyDataGrabber.src.buffers.Buffer import Buffer, DataType

class ListBuffer(Buffer):
    """buffer that stores its values in a capacity limited list
    """

    def __init__(self, id : str = None, capacity : int = 1, data_type : list[DataType] = None, unit : list[str] = None, initial_values : list = None, description : str = None):
        super().__init__(id = id, capacity = capacity, data_type=data_type, initial_values=initial_values, description=description)        
        if self.initial_values is not None:
            self.buffer = self.initial_values
        else:
            self.buffer = list()
        self.lock = threading.RLock()

    def push(self, elements : list):
        with self.lock:
            if hasattr(elements, "__len__"):
                too_many =  len(elements) + self.size() - self.capacity
                if too_many > 0:
                    rest = len(elements) - too_many
                    if rest > 0:
                        self.buffer.extend(elements[0:rest])
                    i = 0
                    while i < too_many:
                        self.__push1(elements[rest + i])
                        i = i + 1
                else:
                    self.buffer.extend(elements)
            else:
                self.__push1(elements)

    def data(self, n : int = 0, persistent : bool = True) -> list:
        with self.lock:
            if n > 0:
                if n > self.size():
                    ListBuffer.LOGGER.warning("buffer only contains " + self.size() + " elements")
                    n = self.size()
                d = self.buffer[0:n]
                if not persistent:
                    del self.buffer[0:n]
                return d
            else:
                d = self.buffer
                if not persistent:
                    self.buffer.clear()
                return d
    
    def size(self) -> int:
        return len(self.buffer)
        
    def __push1(self, element : any):
        """private function for inserting and removing an object if necessary

        Args:
            object (any): a buffer object / sample
        """
        with self.lock:
            if self.size() == self.capacity:
                self.buffer.pop(0)
            
            self.buffer.append(element)