from ..Action import Action


class StopAction(Action):
    """
    An action that stops the state machine.
    """
    
    def execute(self):
        """
        Execute the stop action.
        """
        self.deactivate()
        print(f"Action {self.id} executed. State set to {self.state}.")
        return