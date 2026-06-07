from abc import ABC
from dataclasses import dataclass, field, fields
from typing import Any
import uuid
from loguru import logger

@dataclass
class DataModel(ABC):
    """ base class for data models, which are used to define computational methods, as well as the properties of the model itself.
    The data model can be used to build physics based models, data models for web ui, cad configurators and more ... 
    For the UI generation, the following metadata properties are used:
    - `ui_type`: defines the type of the UI element to be used for this property, e.g. table, plot, dropdown, slider, etc.
    - `ui_options`: defines the options for the UI element, e.g. for dropdowns, the options to be displayed
    - `ui_group`: defines the group number for the UI element in order to group them with other properties in a expandable section in the frontend
    - `ui_order`: defines the order of the UI element in the frontend, lower numbers are displayed first
    - `ui_column`: defines the column number of the UI element in the frontend, if the frontend supports multiple columns, this can be used to display properties side by side
    """
    
    model_id : str = field(default_factory=lambda: str(uuid.uuid4()), metadata={"description": "unique model id in UUID schema", "hidden": False})
    alias : str = field(default=None, metadata={"description": "short name of the model, must not be unique across sessions, but within sessions", "hidden": False})
    version : str = field(default=None, metadata={"description": "version of the model", "hidden": False})
    language : str = field(default=None, metadata={"description": "language code, in order to select language corresponding outputs", "hidden": False})
        
    def set_property(self, property_name : str, value : Any):
        """ sets the property specified by `property_name` to the given `value`

        Args:
            property_name (str): name of the property
            value (Any): any given value that conforms with the property datatype
        """
        if self.has_property(property_name):
            setattr(self, property_name, value)
        else:
            logger.error(f"no property '{property_name}' in {self.__class__.__name__}")

    def set_properties(self, property_value_pairs : dict[str, Any]):
        for k, v in property_value_pairs.items():
            self.set_property(k, v)
    
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
        """
        returns the data model as dictionary, None values are ignored    

        Args:
            with_hidden (bool, optional): ignores the hidden fields. Defaults to False.

        Returns:
            dict: returns a dictionary
        """
        result = {}
        for f in fields(self):
            # check if hidden
            is_hidden = f.metadata.get("hidden", False)
            if not with_hidden and is_hidden:
                continue
            v = getattr(self, f.name)
            if v is not None:
                result[f.name] = v
        return result
    
    def get_model_class(self) -> str:
        """
            Get the fully qualified class name of the model.
            This method returns the complete module path and class name of the current 
            instance, which can be used for serialization, logging, or dynamic class 
            instantiation.
                str: The fully qualified class name in the format 'module.ClassName'.
                    For example: 'pydag.services.datamodel.DataModel.DataModel'
            
            Returns:
                str: fully qualified class name
        """
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"