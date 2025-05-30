from __future__ import annotations
from dataclasses import dataclass, field
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.mappings.ObserverThread import ObserverThread
from PyDataGrabber.mappings.ThreadType import ThreadType
from PyDataGrabber.services.Service import Service
from PyDataGrabber.services.ServiceException import ServiceException
from PyDataGrabber.statemachine.Action import Action
from PyDataGrabber.statemachine.Node import Node
from PyDataGrabber.statemachine.State import State
from PyDataGrabber.statemachine.StatemachineException import StatemachineException
from PyDataGrabber.statemachine.StatemachineObserver import StatemachineObserver
from PyDataGrabber.statemachine.Transition import Transition


@dataclass
class StatemachineService(Service):
    
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})    
    start_node_id : str = field(default=None, metadata={"description": "ID of the start node in the statemachine service"})
    nodes : dict[str, Node] = field(default_factory=dict[str, Node](), metadata={"description": "dictionary of nodes in the statemachine service"})
    thread_type : str = field(default=ThreadType.INSTANT.value, metadata={"description": ""})
    
    def __init__(self):
        super().__init__()
        self.observer_thread : ObserverThread = None
        self.nodes : dict[str, Node] = dict()
        self.actions : dict[str, Action] = dict()
        self.transitions : dict[str, Transition] = dict()
        self.start_action : Action = None
        self.is_running = False

    def install(self, grabber : Grabber = None):
        super().install(grabber)
        if self.start_action is None:
            if self.start_node_id is None:
                raise StatemachineException("No start action can be found!")
            else:
                if self.start_node_id in self.nodes:
                    self.start_action = self.nodes[self.start_node_id]
                else:
                    raise StatemachineException("the specified start node id cannot be found among nodes")            
        for node in self.nodes.values():
            node.install(grabber)
        self.connect_nodes()
    
    def assemble(self, node : Node):
        if isinstance(node, Transition):
            if not node.id in self.transitions.values():
                self.transitions[node.id] = node
                for node2 in node.children:
                    self.assemble(node2)
        elif isinstance(node, Action):
            if not node in self.actions.values():
                self.actions[node.id] = node
                for node2 in node.children:
                    self.assemble(node2)
            else:
                if len(self.transitions) == 0:
                    raise StatemachineException("this " + self.name() + " network causes a " + RecursionError.__name__ + "! Make sure to break your loop Statemachine Network with a " + Transition.cname() + " or change the network layout.")
        
    def start(self):
        if self.start_action is None:
            raise ServiceException("Start node ID must be set before starting the statemachine service.")
        if not isinstance(self.nodes[self.start_action.id], Action):
            raise ServiceException(f"Node with ID {self.start_node_id} is not a valid Action Node instance.")        
        self.assemble(self.start_action)
        self.observer_thread = ObserverThread(ObserverThread.unique_id(), ThreadType.ONLY_ONCE, 0)
        observer = StatemachineObserver(self)
        self.observer_thread.add_observer(observer)
        self.observer_thread.start()

    def stop(self):
        self.is_running = False
    
    def add_node(self, node : Node):
        self.nodes[node.id] = node
        
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
                    
    def has_active_actions(self) -> bool:
        for action in self.actions.values():
            if action.state == State.ACTIVE:
                return True
        return False
    
    def has_active_transitions(self) -> bool:
        for transition in self.transitions.values():
            if transition.state == State.ACTIVE:
                return True
        return False
    
    def node_by_id(self, id) -> Node:
        if id in self.actions:
            return self.actions[id]
        if id in self.transitions:
            return self.transitions[id]
        return None
        
    def activate(self, action : Action):
        action.activate()
    
    def deactivate(self, action: Action):
        action.deactivate()     