from abc import abstractmethod

from PyDataGrabber.statemachine.Node import Node


class Transition(Node):
    
    @abstractmethod
    def check(self) -> bool:
        pass