from dataclasses import dataclass, field
from ...adapters.WriteAdapter import WriteAdapter
from ..Action import Action
from ..AdapterNode import AdapterNode
from ...nodes.NodeException import NodeException

@dataclass
class AdapterWriteAction(AdapterNode, Action):
    """
    Action to write data with an adapter.
    """
    
    address : str = field(default=None, metadata={"description": "The address to read from the adapter."})
    
    def execute(self):
        """
        Execute the read action on the adapter.
        """
        address_list = [self.address]
        buffer_dict = {self.buffer.id: self.buffer}
        if isinstance(self.adapter, WriteAdapter):
            self.adapter.write_to_sink(buffer_dict, address_list, self.n, self.persistent)
        else:
            raise NodeException(f"Adapter {self.adapter.id} is not a WriteAdapter.")