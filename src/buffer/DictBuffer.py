from PyDataGrabber.src.buffer import Buffer

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

        self.data = dict(list)
        for h in headers:
            self.data[h] = []

    def push(self, *args):
        """_summary_

        Args:
            *args (_type_): _description_
        """
        if len(args) == len(self.data):
            k = 0
            for key in self.data:
                self.data[key].append(args[k])
                ++k

        else:
            self.data[self.id].extend(args)


    def push(self, **kwargs):
        """_summary_
        """
        

    def data(self, n=None, persistent=True):
        """returns data from the buffer, if n is specified, then only n samples are retrieved
            if persistent = False, then the retrieved data is removed from list

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (_type_, optional): _description_. Defaults to True.
        """