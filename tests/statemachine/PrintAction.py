from pydatagrabber.statemachine.Action import Action


class PrintAction(Action):
    """
    An action that prints a message when executed.
    """

    def __init__(self):
        super().__init__()
        self.message = None

    def execute(self):
        print(f"Executing PrintAction {self.id}: {self.message}")
        return  # Indicating successful execution