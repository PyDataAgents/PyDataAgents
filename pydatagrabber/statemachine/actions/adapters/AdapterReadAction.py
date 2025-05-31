from dataclasses import dataclass, field
from PyDataGrabber.pydatagrabber.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.pydatagrabber.statemachine.Action import Action
from PyDataGrabber.pydatagrabber.statemachine.AdapterNode import AdapterNode
from PyDataGrabber.pydatagrabber.statemachine.StatemachineException import StatemachineException

@dataclass
class AdapterReadAction(AdapterNode, Action):
    """
    Action to read data from an adapter.
    """
    
    address : str = field(default=None, metadata={"description": "The address to read from the adapter."})
    n : int = field(default=1, metadata={"description": "The number of samples to read."})

    def __init__(self):
        super().__init__()

    def execute(self):
        """
        Execute the read action on the adapter.
        """
        address_list = [self.address]
        buffer_dict = {self.buffer.id: self.buffer}
        if isinstance(self.adapter, ReadAdapter):
            self.adapter.read_from_source(buffer_dict, address_list, self.n)
        else:
            raise StatemachineException(f"Adapter {self.adapter.id} is not a ReadAdapter.")
        