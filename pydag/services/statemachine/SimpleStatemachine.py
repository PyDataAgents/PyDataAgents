from __future__ import annotations
from dataclasses import dataclass


from ...agents.Agent import Agent
from ...nodes.Transition import Transition
from .StatemachineService import StatemachineService
from ..Observer import Observer
from ...nodes.Action import Action


class SimpleStatemachineObserver(Observer):

    def __init__(self, service: SimpleStatemachine):
        super().__init__()
        self._service : SimpleStatemachine = service

    def observe(self):
        for node in self._service.nodes.values():
            if node.is_active():
                if isinstance(node, Action):
                    node.execute()
                if isinstance(node, Transition):
                    if node.check():
                        continue
                    else:
                        break
    
    def unobserve(self):
        return

@dataclass
class SimpleStatemachine(StatemachineService):
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        observer = SimpleStatemachineObserver(self)
        self._observer_thread.add_observer(observer)       