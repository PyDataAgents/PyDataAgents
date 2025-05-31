from ..Transition import Transition


class TrueTransition(Transition):
    """
    A transition that always returns True.
    This is used to test the statemachine without any conditions.
    """

    def __init__(self):
        super().__init__()

    def check(self) -> bool:
        return True  # Always returns True