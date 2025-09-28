from ..Transition import Transition
from .CountAction import CountAction


class CountTransition(Transition):
    """
    A transition that counts the number of times it has been triggered.
    """

    def __init__(self, count_action : CountAction):
        super().__init__()
        self.count_action = count_action
        self.trigger_count = 0
        self.negate = False

    def check(self):
        if (self.negate):
            print(f"Transition {self.id} checks if count {self.count_action.count} does not equal trigger count {self.trigger_count}")
            if self.count_action.count != self.trigger_count:
                return True
            else:
                return False
        else:
            print(f"Transition {self.id} checks if count {self.count_action.count} equals trigger count {self.trigger_count}")
            if self.count_action.count == self.trigger_count:
                return True
            else:
                return False