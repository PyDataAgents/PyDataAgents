from dataclasses import dataclass, field
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.statemachine.Node import Node

@dataclass
class GrabberNode(Node):
    
    grabber_id : str = field(default=None, metadata={"description": "ID of the grabber"})
    
    def __init__(self):
        super().__init__()
        self.grabber : Grabber = None  # Placeholder for the grabber instance