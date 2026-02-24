from ..Transition import Transition


class TrueTransition(Transition):
    """
    A transition that always returns True.
    This is used to test the statemachine without any conditions.
    """

    def _on_check(self) -> bool:
        return True  # Always returns True