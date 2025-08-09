from ..Transition import Transition


class FalseTransition(Transition):
    """
    A transition that always returns False.
    """

    def check(self) -> bool:
        return False  # Always returns False