from dataclasses import dataclass
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class AgentNode(Node):
    
    def __post_init__(self):
        super().__post_init__()
        self.agent : Agent = None  # Placeholder for the agent instance
        
    def install(self, agent : Agent = None):
        super().install(agent)
        self.agent : Agent = agent
        
    def uninstall(self, agent : Agent = None):
        super().uninstall()
        self.agent : Agent = None