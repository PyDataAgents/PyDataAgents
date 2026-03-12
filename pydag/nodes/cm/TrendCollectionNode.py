from dataclasses import dataclass, field

from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode


@dataclass
class TrendCollectionNode(BufferNode, Action):
    """ This `BufferNode` collects windowed data of the linked parents of specified size `n` with the current timestamp as key prefix to the original key.
    Whenever it is executed it generates a new window to keep (up to `max_windows`). If the maximum number of windows are reached, it discards the one closest to any other window, based on timestamp.

    Base Classes:
        BufferNode (_type_): _description_
        Action (_type_): _description_
    """

    max_windows : int = field(default=10, metadata={"description": "number of windows to keep"})
    
    def _on_execute(self):
        d = self.get_parent_data()
        
        