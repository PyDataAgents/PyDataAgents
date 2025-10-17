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
class SimpleActionService(StatemachineService):

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
    
    def connect_nodes(self):
        """
        Connect nodes in the statemachine service.
        This method should be called after all nodes have been added to the service.
        """
        for node in self.nodes:
            if len(node.children) == 0 and len(node.parents) == 0:
                for child_id in node.child_ids:
                    if child_id in self.nodes:
                        node.add_child(self.nodes[child_id])
                    else:
                        raise ServiceException(f"Child node with ID {child_id} not found for node {node.id}.")
            
    def start(self):
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=ThreadType[self.thread_type])
        observer = SimpleActionObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()

    def stop(self):
        self.is_running = False
        
    def add_node(self, node : Node):
        self.nodes.append(node)
        
    def remove_node(self, node_id : str):
        self.nodes = [node for node in self.nodes if node.id != node_id]    