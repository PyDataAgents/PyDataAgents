from PyDataGrabber.pydatagrabber.statemachine.Action import Action


class CountAction(Action):
    """
    Action that counts the number of times it has been called.
    """

    def __init__(self):
        super().__init__()
        self.count = 0

    def execute(self):
        self.count += 1
        print(f"Action {self.id} executed {self.count} times.")