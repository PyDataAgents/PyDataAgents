from abc import abstractmethod
import time


from ..agents.Agent import Agent
from ..agents.AgentStates import AgentElementState, NodeState
from .Node import Node


class Transition(Node):
    """A `Transition` `Node` that defines conditions for state transitions in a state machine.
    """
    
    def _on_install(self, agent : Agent = None):
        return
    
    def _on_uninstall(self, agent : Agent = None): 
        return
        
    def check(self) -> bool:
        self._check_state(NodeState.EXECUTING)
        self._state = NodeState.EXECUTING
        result = self._on_check()
        self._state = AgentElementState.INSTALLED
        self._last_timestamp = time.time_ns()
        return result
      
    @abstractmethod
    def _on_check(self) -> bool:
        """ checking logic defined by each transition sub class 
        """