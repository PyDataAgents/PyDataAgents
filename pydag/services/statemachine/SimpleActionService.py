from dataclasses import dataclass, field
from __future__ import annotations

from loguru import logger

from ...nodes.NodeException import NodeException
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
        for node in self.service.nodes:
            if isinstance(node, Action):
                node.activate()
                if self.service.retry_error_nodes:
                    try:
                        node.execute()
                    except NodeException as e:
                        logger.error(f"Reattempting Node {node.id} execution: {e}")
                        node.execute()
                else:
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
class SimpleActionService(Service):
     
    nodes : list[Action] = field(default_factory=list[Action], metadata={"description": "list of Action nodes to be executed in the statemachine"})
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})    
    thread_type : str = field(default=ThreadType.INSTANT.value, metadata={"description": ""})
    sampling_period : int = field(default=0, metadata={"description": "sampling period that specifies the interval the observer thread should run for"})
    
    def __post_init__(self):
        super().__post_init__()
        self.observer_thread : ObserverThread = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        for node in self.nodes:
            node.install(agent)
            
    def start(self):
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=ThreadType[self.thread_type])
        observer = SimpleActionObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()

    def stop(self):
        self.is_running = False