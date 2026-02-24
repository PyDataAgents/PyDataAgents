from ..Action import Action


class PrintAction(Action):
    """
    An action that prints a message when executed.
    """

    def __post_init__(self):
        super().__post_init__()
        self.message = None

    def _on_execute(self):
        print(f"Executing PrintAction {self.id}: {self.message}")
        return  # Indicating successful execution