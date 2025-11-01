from __future__ import annotations
from dataclasses import dataclass, field

from loguru import logger

from ...nodes.Transition import Transition
from .StatemachineService import StatemachineService
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ...nodes.Action import Action


class SimpleStatemachineObserver(Observer):

    def __init__(self, service: SimpleStatemachine):
        super().__init__()
        self.service = service

    def observe(self):
        for node in self.service.nodes.values():
            if isinstance(node, Action):
                node.activate()
                node.execute()
                node.deactivate()
            if isinstance(node, Transition):
                if node.check():
                    continue
                else:
                    break
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        if self.service.is_running:
            self.service.stop()

@dataclass
class SimpleStatemachine(StatemachineService):
          
    def start(self):
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=ThreadType[self.thread_type])
        observer = SimpleStatemachineObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()  