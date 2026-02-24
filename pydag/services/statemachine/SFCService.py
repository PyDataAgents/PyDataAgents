from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING


from ...agents.AgentStates import AgentElementState, ServiceState
from ...nodes.utils.StopAction import StopAction
from .StatemachineService import StatemachineService
from ...nodes.Action import Action
from ...nodes.Node import Node
from .StatemachineException import StatemachineException
from ...nodes.Transition import Transition
from ..Observer import Observer
from ...nodes.utils.JoinTransition import JoinTransition

if TYPE_CHECKING:
    from ...agents.Agent import Agent

class SFCObserver(Observer):
    """
    Observer for the SFCService.
    This observer is be used to start the statemachine in a separate thread
    """
     
    def __init__(self, statemachine: SFCService):
        super().__init__()
        self._statemachine = statemachine

    def observe(self):
        first_node = next(iter(self._statemachine.nodes.values()))
        if isinstance(first_node, Action):
            self._statemachine.activate(first_node)
        elif isinstance(first_node, Transition):
            first_node.set_active(True)
        while (self._statemachine.get_state() == ServiceState.RUNNING and (self._statemachine.has_active_actions() or self._statemachine.has_active_transitions())):
            # execute active actions
            for action in self._statemachine.get_actions().values():
                if (action.is_active() or (action.get_state() == AgentElementState.ERROR and self._statemachine.retry_error_nodes)):
                    action.execute()
                    for node in action.get_children():
                        if isinstance(node, Transition):
                            node.set_active(True)
                        if isinstance(node, JoinTransition):
                            node.visited_from_parents[action.id] = action.id
                            
            # go through transitions to check               
            for transition in self._statemachine.get_transitions().values():
                if (transition.is_active() or (transition.get_state() == AgentElementState.ERROR and self._statemachine.retry_error_nodes)):
                    if transition.check():
                        # deactivate parent actions
                        for node in transition.get_parents():
                            if isinstance(node, Action):
                                self._statemachine.deactivate(node)
                        # activate child actions and add new transitions
                        for node in transition.get_children():
                            if isinstance(node, Action):
                                self._statemachine.activate(node)
                            elif isinstance(node, Transition):
                                node.set_active(True)
                    
                    # deactivate the transition itself
                    transition.set_active(False)
        self._statemachine.stop()
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        return

@dataclass
class SFCService(StatemachineService):
    
    retry_error_nodes : bool = field(default=False, metadata={"description" : "Statemachine object containing actions and transitions to go through to represent a state machine program flow"})    
    
    def __post_init__(self):
        super().__post_init__()
        self._actions : dict[str, Action] = dict()
        self._transitions : dict[str, Transition] = dict()

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        first_node = next(iter(self.nodes.values()))
        self._assemble(first_node)
        observer = SFCObserver(self)
        self._observer_thread.add_observer(observer)
    
    def _assemble(self, node : Node):
        if isinstance(node, Transition):
            # deactivate transition at the beginning
            node.set_active(False)
            if not node.id in self._transitions.values():
                self._transitions[node.id] = node
                for node2 in node.get_children():
                    self._assemble(node2)
        elif isinstance(node, Action):
            # deactivate action at the beginning
            node.set_active(False)
            if not node in self._actions.values():
                self._actions[node.id] = node
                for node2 in node.get_children():
                    self._assemble(node2)
            else:
                if len(self._transitions) == 0:
                    # check for stop action
                    last_node = next(reversed(self.nodes.values()))
                    if not isinstance(last_node, StopAction):
                        raise StatemachineException("this " + self.name() + " network causes a " + RecursionError.__name__ + "! Make sure to break your loop " + self.cname() +  " Network with a " + Transition.cname() + ", include a " + StopAction.cname() + " at the end of your network or change the network layout.")
                                   
    def has_active_actions(self) -> bool:
        for action in self._actions.values():
            if action.is_active():
                return True
        return False
    
    def has_active_transitions(self) -> bool:
        for transition in self._transitions.values():
            if transition.is_active():
                return True
        return False
            
    def activate(self, action : Action):
        action.set_active(True)
        for node in action.get_children():
            if isinstance(node, Action):
                self.activate(node)
            
    def deactivate(self, action: Action):
        action.set_active(False)
        for node in action.get_parents():
            if isinstance(node, Action):
                self.deactivate(node)   
        
    def remove_node(self, node_id : str):
        super().remove_node(node_id)
        if node_id in self._actions:
            del self._actions[node_id]        
        if node_id in self._transitions:
            del self._transitions[node_id]
            
    def get_transitions(self) -> dict[str, Transition]:
        return self._transitions
    
    def get_actions(self) -> dict[str, Action]:
        return self._actions