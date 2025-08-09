from abc import abstractmethod
from ..agents.AgentElement import AgentElement


class Observer(AgentElement):
    
    def __init__(self):
        super().__init__()
                
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def unobserve(self):
        pass
        

    