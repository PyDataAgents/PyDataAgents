from __future__ import annotations
from dataclasses import dataclass

from ..ObserverException import ObserverException
from .StatemachineService import StatemachineService
from ..Observer import Observer
from ...nodes.Action import Action


class SimpleActionObserver(Observer):

    def __init__(self, service: SimpleActionService):
        super().__init__()
        self._service : SimpleActionService = service

    def observe(self):
        for node in self._service.nodes.values():
            if node.is_active() and isinstance(node, Action):
                try:
                    node.execute()
                except Exception as e:
                    raise ObserverException(f"Error executing action '{node.name}': {str(e)}") from e

    def unobserve(self):
        return

@dataclass
class SimpleActionService(StatemachineService):
    """ `Service` for executing any number of `Action`s in sequence
    """
         
    def _on_install(self, agent = None):
        super()._on_install(agent)
        observer = SimpleActionObserver(self)
        self._observer_thread.add_observer(observer) 