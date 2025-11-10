from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ..Service import Service
from ..ServiceException import ServiceException
from ...nodes.Action import Action
from ...nodes.Node import Node
from .StatemachineException import StatemachineException
from ...nodes.Transition import Transition
from ...mappings.Observer import Observer

if TYPE_CHECKING:
    from ...agents.Agent import Agent
    
class StatemachineObserver(Observer):
    """
    Observer for the StatemachineService.
    This observer is be used to start the statemachine in a separate thread
    """
        
    def __init__(self, statemachine: StatemachineService):
        super().__init__()
        self.statemachine = statemachine

    def observe(self):
        self.statemachine.start_action.activate()
        self.statemachine.is_running = True
        if self.statemachine.is_running:
            # go through all nodes
            self._process_node(self.statemachine.start_action)
        self.statemachine.is_running = False
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        if self.statemachine.is_running:
            self.statemachine.stop()
            
    def _process_node(self, node : Node):
        if isinstance(node, Action):
            node.execute()
            for child in node.children:
                self._process_node(child)
        elif isinstance(node, Transition):
            if node.check():
                for child in node.children:
                    self._process_node(child)
            

@dataclass
class StatemachineService(Service):
    
    nodes : dict[str, Node] = field(default_factory=dict[str, Node], metadata={"description": "dictionary of nodes in the statemachine service"})
    thread_type : str = field(default=ThreadType.INSTANT.value, metadata={"description": ""})
    sampling_period : int = field(default=0, metadata={"description": "sampling period that specifies the interval the observer thread should run for"})
    
    def __post_init__(self):
        super().__post_init__()
        self.observer_thread : ObserverThread = None
        self.nodes : dict[str, Node] = dict()
        self.is_running = False

    def install(self, agent : Agent = None):
        super().install(agent)
        for node in self.nodes.values():
            node.install(agent)
        self.connect_nodes()
        
    @abstractmethod    
    def start(self):
        pass
        
    def stop(self):
        self.is_running = False
        if self.observer_thread is not None:
            self.observer_thread.stop()
    
    def add_node(self, node : Node):
        self.nodes[node.id] = node 
        
    def remove_node(self, node_id : str):
        if node_id in self.nodes:
            del self.nodes[node_id] 
        
    def connect_nodes(self):
        """
        Connect nodes in the statemachine service.
        This method should be called after all nodes have been added to the service.
        """
        for node in self.nodes.values():
            if len(node.children) == 0 and len(node.parents) == 0:
                for child_id in node.child_ids:
                    if child_id in self.nodes:
                        node.add_child(self.nodes[child_id])
                    else:
                        raise ServiceException(f"Child node with ID {child_id} not found for node {node.id}.")
        
    def node_by_id(self, id) -> Node:
        if id in self.nodes:
            return self.nodes[id]
        return None