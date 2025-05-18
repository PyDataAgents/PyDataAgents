from dataclasses import dataclass, field
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.statemachine.Action import Action
from PyDataGrabber.src.statemachine.JoinTransition import JoinTransition
from PyDataGrabber.src.statemachine.Node import Node
from PyDataGrabber.src.statemachine.State import State
from PyDataGrabber.src.statemachine.StatemachineException import StatemachineException
from PyDataGrabber.src.statemachine.Transition import Transition

@dataclass
class Statemachine(GrabberElement):
    
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})
    
    def __init__(self, start_action : Action): 
        self.actions : dict[str, Action] = dict()
        self.transitions : dict[str, Transition] = dict()
        self.start_action = start_action
        self.is_running = False
        
    def assemble(self, node : Node):
        if isinstance(node, Transition):
            if not node.id in self.transitions:
                self.transitions[node.id] = node
                for node2 in node.children:
                    self.assemble(node2)
        elif isinstance(node, Action):
            if not node in self.actions:
                self.actions[node.id] = node
                for node2 in node.children:
                    self.assemble(node2)
            else:
                if len(self.transitions) == 0:
                    raise StatemachineException("this " + self.name() + " network causes a " + RecursionError.__name__ + "! Make sure to break your loop Statemachine Network with a " + Transition.cname() + " or change the network layout.")
        
    def start(self):
        self.assemble(self.start_action)
        self.start_action.activate()
        while (self.is_running and (self.has_active_actions() or self.has_active_transitions())):
            # execute active actions
            for action in self.actions.values():
                if (action.state == State.ACTIVE or (action.state == State.ERROR and self.retry_error_nodes)):
                    action.execute()
                    for node in action.children:
                        if isinstance(node, Transition):
                            node.state = State.ACTIVE
                        if isinstance(node, JoinTransition):
                            node.visited_from_parents[action.id] = action.id
                            
            # go through transitions to check               
            for transition in self.transitions.values():
                if transition.state == State.ACTIVE:
                    if transition.check():
                        # deactivate parent actions
                        for node in transition.parents:
                            if isinstance(node, Action):
                                node.deactivate()
                        # activate child actions and add new transitions
                        for node in transition.children:
                            if isinstance(node, Action):
                                self.activate(node)
                            elif isinstance(node, Transition):
                                node.state = State.ACTIVE
                    
                    # deactivate the transition itself
                    transition.state = State.INACTIVE
    
    def stop(self):
        self.is_running = False
        
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