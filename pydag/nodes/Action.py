from abc import abstractmethod
from .Node import Node
from .State import State


class Action(Node):
    
    def activate(self):
        self.state = State.ACTIVE
        for node in self.children:
            if isinstance(node, Action):
                node.activate()
    
    def deactivate(self):
        self.state = State.INACTIVE
        for node in self.parents:
            if isinstance(node, Action):
                node.deactivate()
    
    @abstractmethod
    def execute(self):
        """
        method for execution of the `Action`
        """