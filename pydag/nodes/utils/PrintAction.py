from dataclasses import dataclass

from ..Action import Action


@dataclass
class PrintAction(Action):
    """
    An action that prints a message when executed.
    """

    message : str = None
    
    def _on_execute(self):
        print(f"Executing PrintAction {self.id}: {self.message}")
        return  # Indicating successful execution