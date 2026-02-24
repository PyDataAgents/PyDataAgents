from ..Action import Action


class StartAction(Action):
    """
    An action that starts the state machine.
    """
    
    def _on_execute(self):
        return