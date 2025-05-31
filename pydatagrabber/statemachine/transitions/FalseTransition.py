from ..Transition import Transition


class FalseTransition(Transition):
    """
    A transition that always returns False.
    """

    def __init__(self):
        super().__init__()

    def check(self) -> bool:
        return False  # Always returns False