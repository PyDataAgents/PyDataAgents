from abc import abstractmethod
from ..agents.AgentElement import AgentElement


class Observer(AgentElement):
                    
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def unobserve(self):
        pass
        

    