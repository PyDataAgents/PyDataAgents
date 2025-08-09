from dataclasses import dataclass
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class GrabberNode(Node):
    
    def __init__(self):
        super().__init__()
        self.grabber : Agent = None  # Placeholder for the grabber instance
        
    def install(self, grabber : Agent = None):
        super().install(grabber)
        self.grabber : Agent = grabber
        
    def deinstall(self, grabber : Agent = None):
        super().deinstall()
        self.grabber : Agent = None