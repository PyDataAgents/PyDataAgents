from abc import abstractmethod
import time


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
        self.begin_execution()
        try:
            result = self._on_check()
            if result:
                self.mark_transition()
            return result
        except Exception:
            self.mark_interrupted()
            raise
        finally:
            self.end_execution()
      
    @abstractmethod
    def _on_check(self) -> bool:
        """ checking logic defined by each transition sub class 
        """
