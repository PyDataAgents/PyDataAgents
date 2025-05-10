import json
from PyDataGrabber.src.buffer import Buffer

class ListBuffer(Buffer):
    """buffer that stores its values in a capacity limited list

    Args:
        Buffer (_type_): _description_
    """

    def __init__(self, id, capacity):
        """constructor

        Args:
            id (_type_): _description_
            capacity (_type_): _description_
            headers (_type_): names of the builtin list for data buffering
        """
        super().__init__(id, capacity)
        self.data = list()

    def push(self, *args):
        """_summary_

        Args:
            *args (_type_): _description_
        """
        tooMany =  self.capacity - (len(args) + self.size())
        if tooMany > 0:
            rest = len(args) - tooMany
            if rest > 0:
                self.data.extend(args[rest - 1:])
            i = 0
            while i < tooMany:
                self.__push1(args[rest + i])
                ++i
        else:
            self.data.extend(args)

    def data(self, n=None, persistent=True):
        """returns data from the buffer, if n is specified, then only n samples are retrieved
            if persistent = False, then the retrieved data is removed from list

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (_type_, optional): _description_. Defaults to True.
        """

    def json(self, n=None, persistent=True):
        return json.dumps(self.data(n, persistent))        

    def size(self) -> int:
        return len(self.data)
        
    def __push1(self, object):
        if self.size() == self.capacity:
            self.data.pop(0)
        
        self.data.append(object)