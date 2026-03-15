from abc import abstractmethod
import time


from ..agents.AgentStates import NodeState
from .Node import Node


class Action(Node):
        
    def execute(self):
        """
        method for execution of the `Action`
        """
        self.begin_execution()
        try:
            self._on_execute()
        except Exception:
            self.mark_interrupted()
            raise
        finally:
            self.end_execution()
        
        
    @abstractmethod
    def _on_execute(self):
        """
        execution logic defined by each `Action` subclass
        """
            
    def _on_install(self, agent = None):
        return
    
    def _on_uninstall(self, agent = None):
        return
