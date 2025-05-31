import time
from PyDataGrabber.pydatagrabber.buffers.ListBuffer import ListBuffer


class TimedBuffer(ListBuffer):
    """
    A buffer that stores data with timestamps.
    Inherits from ListBuffer.
    """
    
    def __init__(self):
        super().__init__()
        self.timestamps = []  # List to store timestamps corresponding to the data
   
    def push(self, elements : list):
        with self.lock:
            if isinstance(elements, str):
                ts = round(time.time() * 1000)  # Current timestamp in milliseconds
                self.__push_timestamp(elements, ts)
            if hasattr(elements, "__len__"):
                too_many =  len(elements) + self.size() - self.capacity
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
                too_many =  len(elements) + self.size() - self.capacity
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
                        ListBuffer.LOGGER.warning("buffer only contains " + str(self.size()) + " elements")
                        n = self.size()
                    v = self.elements[0:n]
                    t = self.timestamps[0:n]
                    if not persistent:
                        del self.elements[0:n]
                        del self.timestamps[0:n]
                    d = {"values": v, "timestamps": t}
                    return d
                else:
                    v = self.elements
                    t = self.timestamps
                    d = {"values": v, "timestamps": t}
                    if not persistent:
                        self.elements.clear()
                        self.timestamps.clear()
                    return d
            else:
                ListBuffer.LOGGER.warning("buffer is empty")
                return {}
                
    def __push_timestamp(self, element : any, timestamp : int):
        """private function for inserting a timestamp

        Args:
            element (any): a buffer object / sample
            timestamp (int): the timestamp of the element
        """
        with self.lock:
            if self.size() == self.capacity:
                self.timestamps.pop(0)
                self.elements.pop(0)
            
            self.elements.append(element)
            self.timestamps.append(timestamp)