from PyDataGrabber.pydatagrabber.adapter import Adapter

class Adapter1(Adapter):
    """_summary_

    Args:
        Adapter (_type_): _description_
    """
    
    def __init__(self):
        """_summary_"""
        super().__init__()        
        
    def validate(self):
        """
        validate the adapter configuration.
        """
        return

    def install(self):
        """
        install the adapter / initialize object.
        """
        return

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
    
    def isConnected(self):
        """
        check if the adapter is connected to the data source.
        """
        return True
        
    def run(self):
        """_summary_"""
        print(self.id)
    