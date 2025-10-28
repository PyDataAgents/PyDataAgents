from __future__ import annotations
from dataclasses import dataclass, field

from loguru import logger

from .StatemachineService import StatemachineService
from ...services.ServiceException import ServiceException
from ...nodes.NodeException import NodeException
from ...nodes.Node import Node
from ...agents.Agent import Agent
from ...mappings.Observer import Observer
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ...nodes.Action import Action
from ...services.Service import Service


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
          
    def start(self):
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=ThreadType[self.thread_type])
        observer = SimpleActionObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()  