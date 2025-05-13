from PyDataGrabber.src.adapters.Adapter import Adapter

class Adapter1(Adapter):
    """_summary_

    Args:
        Adapter (_type_): _description_
    """
    
    def __init__(self, id=None):
        """_summary_"""
        super().__init__(id)        
        
    def connect(self):
        """
        connect to the data source.
        """
        return True    
    
    def disconnect(self):
        """
        disconnect from the data source.
        """
        return True
        
    def run(self):
        """_summary_"""
        print(self.id)
    