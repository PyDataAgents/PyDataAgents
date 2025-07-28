from typing import Any
from .DataElementAction import DataElementAction


class OutputBufferAction(DataElementAction):
    """
    `DataElementAction` for storing data from `DataElementAction` Pipeline into a specified `Buffer`
    """
        
    def __init__(self):
        super().__init__()        
         
    def transform(self, data: dict = None) -> Any:
        # do nothing, as the InputBufferAction does not transform data
        return