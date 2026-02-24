from dataclasses import dataclass, field

from ..agents.Agent import Agent
from ..services.Service import Service
from .Node import Node
from ..services.statemachine.StatemachineException import StatemachineException

@dataclass
class ServiceNode(Node):
    """
    A class representing a service node in a state machine.
    Inherits from Node and adds functionality specific to service nodes.
    """
    
    service_id: str = field(init=True, default=None, metadata={"description": "ID of the service"})

    def __post_init__(self):
        """
        Initializes the ServiceNode with a name and a service.

        :param name: The name of the service node.
        :param service: The service associated with this node.
        """
        super().__post_init__()
        self._service = None
        
    def _on_install(self, agent : Agent = None):
        if self._service is None:
            if agent.get_service(self.service_id):
                self._service = agent.get_service(self.service_id)
            else:
                raise StatemachineException("No " + Service.cname() + " with id=" + self.service_id + " was found")
    
    def _on_uninstall(self, agent : Agent = None):
        self._service = None
            
    def set_service(self, service : Service):
        """Sets the service for this ServiceNode.

        :param service: The service to be set.
        
        """
        self._service = service
        self.service_id = service.id
    
    def get_service(self) -> Service:
        return self._service