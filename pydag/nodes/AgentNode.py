from dataclasses import dataclass
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class AgentNode(Node):
    
    def __post_init__(self):
        super().__post_init__()
        self._agent : Agent = None  # Placeholder for the agent instance
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._agent : Agent = agent
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall()
        self._agent : Agent = None