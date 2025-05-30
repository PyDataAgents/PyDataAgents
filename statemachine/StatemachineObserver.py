from __future__ import annotations
from typing import TYPE_CHECKING
from PyDataGrabber.mappings.Observer import Observer
from PyDataGrabber.statemachine.Action import Action
from PyDataGrabber.statemachine.JoinTransition import JoinTransition
from PyDataGrabber.statemachine.State import State
from PyDataGrabber.statemachine.Transition import Transition

if TYPE_CHECKING:
    from PyDataGrabber.statemachine.StatemachineService import StatemachineService
    
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
                if transition.state == State.ACTIVE:
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