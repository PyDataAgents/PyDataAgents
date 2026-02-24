from ..Transition import Transition


class FalseTransition(Transition):
    """
    A transition that always returns False.
    """

    def _on_check(self) -> bool:
        return False  # Always returns False