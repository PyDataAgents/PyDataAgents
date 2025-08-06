from typing import Any
from .DataElementAction import DataElementAction


class InputBufferAction(DataElementAction):
    """
    `DataElementAction` for retrieving data from a `Grabber` `Buffer` to a `DataElementAction`.
    """      
        
    def __init__(self):
        super().__init__()
    
    def execute(self):
        # nothing to do here, as the DataElementAction is just a link to an existing buffer
        return
        
    def transform(self, data: dict = None) -> Any:
        # do nothing, as the InputBufferAction does not transform data
        return