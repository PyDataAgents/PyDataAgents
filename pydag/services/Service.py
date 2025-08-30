from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from ..agents.AgentElement import AgentElement


if TYPE_CHECKING:
    from ..agents.Agent import Agent

class Service(AgentElement):
    """abstract base class for agent Services
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.is_running : bool = False
        self.agent : Agent = None
    
    def install(self, agent : Agent = None):
        super().install(agent)
        if self.agent is None:
            self.agent = agent
        
    @abstractmethod
    def start(self):
        self.is_running = True
    
    @abstractmethod
    def stop(self):
        self.is_running = False
    
    
    