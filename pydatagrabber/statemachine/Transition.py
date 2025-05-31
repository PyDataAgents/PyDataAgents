from abc import abstractmethod

from .Node import Node


class Transition(Node):
    
    @abstractmethod
    def check(self) -> bool:
        pass