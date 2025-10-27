from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .StatemachineService import StatemachineService
from ...mappings.ObserverThread import ObserverThread
from ...mappings.ThreadType import ThreadType
from ..Service import Service
from ..ServiceException import ServiceException
from ...nodes.Action import Action
from ...nodes.Node import Node
from .StatemachineException import StatemachineException
from ...nodes.Transition import Transition
from ...mappings.Observer import Observer
from ...nodes.utils.JoinTransition import JoinTransition
from ...nodes.State import State

if TYPE_CHECKING:
    from ...agents.Agent import Agent

class SFCObserver(Observer):
    """
    Observer for the SFCService.
    This observer is be used to start the statemachine in a separate thread
    """
        
    def __init__(self, statemachine: SFCService):
        super().__init__()
        self.statemachine = statemachine

    def observe(self):
        self.statemachine.start_action.activate()
        self.statemachine.is_running = True
        while (self.statemachine.is_running and (self.statemachine.has_active_actions() or self.statemachine.has_active_transitions())):
            # execute active actions
            for action in self.statemachine.actions.values():
                if (action.state == State.ACTIVE or (action.state == State.ERROR and self.statemachine.retry_error_nodes)):
                    action.execute()
                    for node in action.children:
                        if isinstance(node, Transition):
                            node.state = State.ACTIVE
                        if isinstance(node, JoinTransition):
                            node.visited_from_parents[action.id] = action.id
                            
            # go through transitions to check               
            for transition in self.statemachine.transitions.values():
                if (transition.state == State.ACTIVE or (transition.state == State.ERROR and self.statemachine.retry_error_nodes)):
                    if transition.check():
                        # deactivate parent actions
                        for node in transition.parents:
                            if isinstance(node, Action):
                                node.deactivate()
                        # activate child actions and add new transitions
                        for node in transition.children:
                            if isinstance(node, Action):
                                self.statemachine.activate(node)
                            elif isinstance(node, Transition):
                                node.state = State.ACTIVE
                    
                    # deactivate the transition itself
                    transition.state = State.INACTIVE
        self.statemachine.is_running = False
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        if self.statemachine.is_running:
            self.statemachine.stop()

@dataclass
class SFCService(StatemachineService):
    
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})    
    start_action_id : str = field(default=None, metadata={"description": "ID of the start node in the statemachine service"})
    nodes : dict[str, Node] = field(default_factory=dict[str, Node], metadata={"description": "dictionary of nodes in the statemachine service"})
    thread_type : str = field(default=ThreadType.ONLY_ONCE.value, metadata={"description": "the type of ObserverThread to use: ONLY_ONCE | MILLI_SECONDS | SECONDS | INSTANT | TRIGGERED"})
    sampling_period : int = field(default=0, metadata={"description": "sampling period that specifies the interval the observer thread should run for"})
    
    def __post_init__(self):
        super().__post_init__()
        self.observer_thread : ObserverThread = None
        self.nodes : dict[str, Node] = dict()
        self.actions : dict[str, Action] = dict()
        self.transitions : dict[str, Transition] = dict()
        self.start_action : Action = None
        self.is_running = False

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.start_action is None:
            if self.start_action_id is None:
                raise StatemachineException("No start action can be found!")
            else:
                if self.start_action_id in self.nodes:
                    self.start_action = self.nodes[self.start_action_id]
                else:
                    raise StatemachineException("the specified start node id cannot be found among nodes")            
        for node in self.nodes.values():
            node.install(agent)
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
            raise ServiceException(f"Node with ID {self.start_action_id} is not a valid Action Node instance.")        
        self.assemble(self.start_action)
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=ThreadType[self.thread_type], sampling_period=self.sampling_period)
        observer = SFCObserver(self)
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
            for child_id in node.child_ids:
                if child_id in self.nodes:
                    if not node.has_child(child_id):
                        node.add_child(self.nodes[child_id])
                else:
                    raise ServiceException(f"Child node with ID {child_id} not found for node {node.id}.")
       
    def set_start_action(self, action : Action):
        """sets the start action and this `Service` `start_action_id` property
        <br>this method must be used in scripts when building `StatemachineService`s
        
        Args:
            action (Action): `Action` instance
        """
        self.start_action = action
        self.start_action_id = action.id
                    
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