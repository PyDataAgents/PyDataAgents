from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class CopyDataAction(BufferNode, Action):
    """ `Action` that makes a copy of the data in all parent `Buffer`s found amongst this `Node`s parents.
        If this `Node`'s parents contains more than one `BufferNode`, all data is merged and copied.
        Before this `Node`s `Buffer` is filled, all other elements are cleared.
    """
    
    clear_first : bool = field(default=True, metadata={"description": "if set to true, this Buffer's content is cleared before copying"})

    def _on_execute(self):
        data = self.get_parent_data()
        if self.clear_first:
            self._buffer.clear()
        self.add_data(data)