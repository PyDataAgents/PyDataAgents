from abc import abstractmethod
import time


from ..agents.AgentStates import NodeState
from .Node import Node


class Action(Node):
        
    def execute(self):
        """
        method for execution of the `Action`
        """
        self._state = NodeState.EXECUTING
        self._on_execute()
        self._state = NodeState.IDLE
        self._last_timestamp = time.time_ns()
        
        
    @abstractmethod
    def _on_execute(self):
        """
        execution logic defined by each `Action` subclass
        """
            
    def _on_install(self, agent = None):
        return
    
    def _on_uninstall(self, agent = None):
        return
