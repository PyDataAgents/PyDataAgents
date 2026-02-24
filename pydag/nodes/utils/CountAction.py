from ..Action import Action


class CountAction(Action):
    """
    Action that counts the number of times it has been called.
    """

    def __post_init__(self):
        super().__post_init__()
        self.count = 0

    def _on_execute(self):
        self.count += 1
        print(f"Action {self.id} executed {self.count} times.")