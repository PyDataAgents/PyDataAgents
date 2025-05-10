import json
from PyDataGrabber.src.buffers.Buffer import Buffer

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

    def data(self, n=None, persistent=True) -> dict:
        """returns data from the buffer, if n is specified, then only n samples are retrieved
            if persistent = False, then the retrieved data is removed from list

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (_type_, optional): _description_. Defaults to True.
        """
        d = {}
        d['values'] = self.data
        return d

    def json(self, n=None, persistent=True):
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
        return len(self.data)
        
    def __push1(self, object):
        """_summary_

        Args:
            object (_type_): _description_
        """        
        if self.size() == self.capacity:
            self.data.pop(0)
        
        self.data.append(object)