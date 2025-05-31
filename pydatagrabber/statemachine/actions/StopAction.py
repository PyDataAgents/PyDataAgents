from PyDataGrabber.pydatagrabber.statemachine.Action import Action


class StopAction(Action):
    """
    An action that stops the state machine.
    """

    def __init__(self):
        super().__init__()

    def execute(self):
        """
        Execute the stop action.
        """
        self.deactivate()
        print(f"Action {self.id} executed. State set to {self.state}.")
        return