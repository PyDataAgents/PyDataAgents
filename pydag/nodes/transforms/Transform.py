from abc import abstractmethod


from ...agents.AgentElement import AgentElement

class Transform(AgentElement):
       
    def _on_install(self, agent = None):
        return
    
    def _on_uninstall(self, agent = None):
        return  
        
    @abstractmethod
    def transform(self, data : dict) -> dict:
        """
        Abstract method to transform data.
        This method should be implemented in the child class.
        
        Args:
            data: The input data to be transformed.
        
        Returns:
            Transformed data.
        """