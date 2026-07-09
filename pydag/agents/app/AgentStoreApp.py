from dataclasses import dataclass

from ..AgentStore import AgentStore


@dataclass
class AgentStoreApp:
    """ Application that stores an `AgentStore` and provides a REST API and UI based on configuration settings """
    
    def __init__(self):
        self._agent_store : AgentStore = None