from dataclasses import dataclass
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.statemachine.Node import Node

@dataclass
class GrabberNode(Node):
    
    def __init__(self):
        super().__init__()
        self.grabber : Grabber = None  # Placeholder for the grabber instance
        
    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.grabber : Grabber = grabber
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall()
        self.grabber : Grabber = None