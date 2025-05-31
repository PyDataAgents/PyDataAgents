from dataclasses import dataclass, field
from PyDataGrabber.pydatagrabber.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.pydatagrabber.statemachine.Action import Action
from PyDataGrabber.pydatagrabber.statemachine.AdapterNode import AdapterNode
from PyDataGrabber.pydatagrabber.statemachine.StatemachineException import StatemachineException

@dataclass
class AdapterWriteAction(AdapterNode, Action):
    """
    Action to write data with an adapter.
    """
    
    address : str = field(default=None, metadata={"description": "The address to read from the adapter."})
    n : int = field(default=1, metadata={"description": "The number of samples to read."})
    persistent : bool = field(default=False, metadata={"description": "If True, the data will be stored in a persistent buffer."})
    
    def __init__(self):
        super().__init__()

    def execute(self):
        """
        Execute the read action on the adapter.
        """
        address_list = [self.address]
        buffer_dict = {self.buffer.id: self.buffer}
        if isinstance(self.adapter, WriteAdapter):
            self.adapter.write_to_sink(buffer_dict, address_list, self.n, self.persistent)
        else:
            raise StatemachineException(f"Adapter {self.adapter.id} is not a WriteAdapter.")