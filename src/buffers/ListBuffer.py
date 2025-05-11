import json
import threading
from PyDataGrabber.src.buffers.Buffer import Buffer

class ListBuffer(Buffer):
    """buffer that stores its values in a capacity limited list

    Args:
        Buffer (_type_): _description_
    """

    def __init__(self, id: str = None, capacity: int = 1, initial_values: list = None, description: str = None):
        """constructor

        Args:
            id (str): _description_
            capacity (int): _description_
            initial_values (list): initial values to insert into the list
        """
        super().__init__(id, capacity, initial_values, description)        
        if initial_values != None:
            self.buffer = list(initial_values)
        else:
            self.buffer = list()
        self.lock = threading.RLock()

    def push(self, objects):
        """_summary_

        Args:
            *args (_type_): _description_
        """
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

    def data(self, n=0, persistent=True) -> dict:
        """returns data from the buffer, if n is specified, then only n samples are retrieved
            if persistent = False, then the retrieved data is removed from list

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (_type_, optional): _description_. Defaults to True.
        """
        with self.lock:
            if n > 0:
                if n > self.size():
                    ListBuffer.LOGGER.warning("buffer only contains " + self.size() + " objects")
                    n = self.size()
                d = {}
                d["values"] = self.buffer[0:n]
                if not persistent:
                    del self.buffer[0:n]
                return d
            else:
                d = {}
                d["values"] = self.buffer
                if not persistent:
                    self.buffer.clear
                return d

    def json(self, n=0, persistent=True):
        """_summary_

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        return json.dumps(self.data(n, persistent))  

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.json()      

    def size(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        return len(self.buffer)
        
    def __push1(self, object):
        """_summary_

        Args:
            object (_type_): _description_
        """
        with self.lock:        
            if self.size() == self.capacity:
                self.buffer.pop(0)
            
            self.buffer.append(object)