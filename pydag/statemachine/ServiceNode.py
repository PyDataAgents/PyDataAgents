from dataclasses import dataclass, field

from ..agents.Agent import Agent
from ..services.Service import Service
from .Node import Node
from .StatemachineException import StatemachineException

@dataclass
class ServiceNode(Node):
    """
    A class representing a service node in a state machine.
    Inherits from Node and adds functionality specific to service nodes.
    """
    
    service_id: str = field(init=True, default=None, metadata={"description": "ID of the service"})

    def __init__(self):
        """
        Initializes the ServiceNode with a name and a service.

        :param name: The name of the service node.
        :param service: The service associated with this node.
        """
        super().__init__()
        self.service = None
        
    def install(self, agent : Agent = None):
        super().install()
        if self.service is None:
            if self.service_id in agent.mapping_store:
                self.service = agent.service_store[self.service_id]
            else:
                raise StatemachineException("No " + Service.cname() + " with id=" + self.service_id + " was found")
            
    def deinstall(self, agent : Agent = None):
        super().deinstall()
        self.service : Service = None