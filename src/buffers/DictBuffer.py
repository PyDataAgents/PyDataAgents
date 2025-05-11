from PyDataGrabber.src.buffers import Buffer
from PyDataGrabber.src.buffers.BufferException import BufferException

class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data

    Args:
        Buffer (_type_): _description_
    """

    def __init__(self, id, capacity, headers=None):
        """constructor

        Args:
            id (_type_): _description_
            capacity (_type_): _description_
            headers (_type_): names of the builtin list for data buffering
        """
        super().__init__(id, capacity)
        if headers == None:
            headers = (self.id)

        self.buffer = dict(list)
        for h in headers:
            self.buffer[h] = []

    def push(self, *args):
        """_summary_

        Args:
            *args (_type_): _description_
        """
        if len(args) == len(self.buffer):
            k = 0
            for key in self.buffer:
                self.buffer[key].append(args[k])
                k = k + 1

        else:
            raise BufferException("input must be the same length as dictionaries")


    def push(self, **kwargs):
        """_summary_
        """
        if len(kwargs.items()) != len(self.buffer):
            raise BufferException("input must be the same length as dictionaries")
        
        for k, values in kwargs.items():
            print(k, values)
            tooMany =  self.capacity - (len(values) + self.size())
            if tooMany > 0:
                rest = len(values) - tooMany
                if rest > 0:
                    self.buffer.extend(values[rest - 1:])
                i = 0
                while i < tooMany:
                    self.__push1(values[rest + i])
                    i = i + 1
            else:
                self.buffer.extend(values)

        

    def data(self, n=None, persistent=True):
        """returns data from the buffer, if n is specified, then only n samples are retrieved
            if persistent = False, then the retrieved data is removed from list

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (_type_, optional): _description_. Defaults to True.
        """
        return self.buffer