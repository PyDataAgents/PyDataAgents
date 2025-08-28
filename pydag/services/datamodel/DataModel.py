from abc import ABC
from dataclasses import dataclass, fields
from typing import Any
from loguru import logger
from .DataModelService import DataModelObserver

@dataclass
class DataModel(ABC):
    
    def __init__(self, observer : DataModelObserver):
        self.observer = observer
    
    def set_data(self, property_name : str, value : Any):
        if self.has_property(property_name):
            setattr(self, property_name, value)
            self.observer.observe([property_name])
        else:
            logger.error(f"no property '{property_name}' in {self.__class__}")
    
    def has_property(self, property_name) -> bool:
        if hasattr(self, property_name):
            return True
        else:
            return False
    
    def has_value(self, property_name : str) -> bool:
        """ checks whether a property has a proper value != None
        
            Args:
            property_name (str): name of the property to check

        Returns:
            bool: True/False
        """
        if getattr(self, property_name) is not None:
            return True
        else:
            return False
            
    def to_dict(self, with_hidden : bool = False) -> dict:
        """ returns the data model as dictionary    

        Args:
            with_hidden (bool, optional): ignores the hidden fields. Defaults to False.

        Returns:
            dict: _descreturns a dictionary
        """
        result = {}
        for f in fields(self):
            # check if hidden
            is_hidden = f.metadata.get("hidden", False)
            if not with_hidden and is_hidden:
                continue
            result[f.name] = getattr(self, f.name)
        return result