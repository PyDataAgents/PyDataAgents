from abc import abstractmethod


from ..agents.Agent import Agent
from ..agents.AgentStates import NodeState
from .Node import Node


class Transition(Node):
    """A `Transition` `Node` that defines conditions for state transitions in a state machine.
    """
    
    def _on_install(self, agent : Agent = None):
        return
    
    def _on_uninstall(self, agent : Agent = None): 
        return
        
    def check(self) -> bool:
        self._state = NodeState.EXECUTING
        result = self._on_check()
        self._state = NodeState.IDLE    
        return result
      
    @abstractmethod
    def _on_check(self) -> bool:
        """ checking logic defined by each transition sub class 
        """