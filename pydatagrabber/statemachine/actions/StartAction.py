from PyDataGrabber.pydatagrabber.statemachine.Action import Action
from PyDataGrabber.pydatagrabber.statemachine.State import State


class StartAction(Action):
    """
    An action that starts the state machine.
    """

    def __init__(self):
        super().__init__()

    def execute(self):
        self.state = State.INACTIVE
        print(f"Action {self.id} executed. State set to {self.state}.")
        return