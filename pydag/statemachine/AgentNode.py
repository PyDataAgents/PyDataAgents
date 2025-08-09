from dataclasses import dataclass
from ..agents.Agent import Agent
from .Node import Node

@dataclass
class AgentNode(Node):
    
    def __init__(self):
        super().__init__()
        self.agent : Agent = None  # Placeholder for the agent instance
        
    def install(self, agent : Agent = None):
        super().install(agent)
        self.agent : Agent = agent
        
    def deinstall(self, agent : Agent = None):
        super().deinstall()
        self.agent : Agent = None