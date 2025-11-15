from __future__ import annotations
from dataclasses import dataclass

from .StatemachineService import StatemachineService
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...nodes.Action import Action


class SimpleActionObserver(Observer):

    def __init__(self, service: SimpleActionService):
        super().__init__()
        self.service = service

    def observe(self):
        for node in self.service.nodes.values():
            if isinstance(node, Action):
                node.activate()
                node.execute()
                node.deactivate()
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        if self.service.is_running:
            self.service.stop()

@dataclass
class SimpleActionService(StatemachineService):
    """ `Service` for executing any number of `Action`s in sequence
    """
          
    def start(self):
        self.observer_thread = ObserverThread(
            id=ObserverThread.unique_id(),
            thread_type=self.thread_type,
            sampling_period=self.sampling_period
        )
        observer = SimpleActionObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()  