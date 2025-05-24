from dataclasses import dataclass, field

from PyDataGrabber.src.statemachine.Node import Node

@dataclass
class ServiceNode(Node):
    """
    A class representing a service node in a state machine.
    Inherits from Node and adds functionality specific to service nodes.
    """
    
    service_id: str = field(default=None, metadata={"description": "ID of the service"})

    def __init__(self):
        """
        Initializes the ServiceNode with a name and a service.

        :param name: The name of the service node.
        :param service: The service associated with this node.
        """
        super().__init__()
        self.service = None