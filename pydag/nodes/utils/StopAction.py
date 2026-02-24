from ..Node import Node
from ..Action import Action


class StopAction(Action):
    """
    An action that stops the state machine.
    """
    
    def _on_execute(self):
        """
        Execute the stop action.
        """
        # deactivates itself and all parent nodes recursively
        StopAction._deactivate_node(self)
    
    @staticmethod
    def _deactivate_node(node : Node):
        node.set_active(False)
        for pn in node.get_parents():
            StopAction._deactivate_node(pn)
            