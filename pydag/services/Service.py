from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from ..agents.AgentElement import AgentElement


if TYPE_CHECKING:
    from ..agents.Agent import Agent

class Service(AgentElement):
    """abstract base class for Grabber Services
    """
    
    def __init__(self):
        super().__init__()
        self.is_running : bool = False
        self.grabber : Agent = None
    
    def install(self, grabber : Agent = None):
        super().install(grabber)
        self.grabber = grabber
        
    @abstractmethod
    def start(self):
        self.is_running = True
    
    @abstractmethod
    def stop(self):
        self.is_running = False
    
    
    