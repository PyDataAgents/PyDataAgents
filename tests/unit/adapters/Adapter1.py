from pydag.adapters.Adapter import Adapter

class Adapter1(Adapter):
    """_summary_

    Args:
        Adapter (_type_): _description_
    """
    
    def __init__(self):
        """_summary_"""
        super().__init__()        
    
    def _on_install(self, agent = None):
        return
    
    def _on_uninstall(self, agent = None):
        return
        
    def _on_connect(self):
        """
        connect to the data source.
        """
        return True    
    
    def _on_disconnect(self):
        """
        disconnect from the data source.
        """
        return True
        
    def run(self):
        """_summary_"""
        print(self.id)
    