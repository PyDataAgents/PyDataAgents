from __future__ import annotations
from dataclasses import MISSING, fields
import importlib

from ..grabbers.GrabberException import GrabberException

class ClassUtils:
    
    @staticmethod
    def create_class(fully_qualified_class_name):
        """
        Create a class from the class name.
        """
        # Split the fully qualified class name into module and class name
        module_name, class_name = fully_qualified_class_name.rsplit(".", 1)
        Clazz = getattr(importlib.import_module(fully_qualified_class_name), class_name)
        return Clazz
    
    @staticmethod
    def create_instance(fully_qualified_class_name):
        """
        Create an instance of a class from the class name.
        """
        Clazz = ClassUtils.create_class(fully_qualified_class_name)
        return Clazz()
    
    @staticmethod
    def set_property(obj, property_name, value):
        """
        Set a property of an object.
        """
        if hasattr(obj, property_name):
            attr = getattr(obj, property_name)
            if attr is not None:
                from ..grabbers.GrabberElement import GrabberElement
                if isinstance(attr, GrabberElement):
                    if isinstance(value, dict):
                        # If the value is a dictionary, set properties of the GrabberElement
                        if "type" in value:
                            # If the dictionary contains a type, create an instance of that type
                            sub_obj = ClassUtils.create_instance(value["type"])
                            ClassUtils.set_properties(sub_obj, value)
                            setattr(obj, property_name, sub_obj)
                        else:
                            raise GrabberException(f"Expected a dictionary with 'type' for property '{property_name}' of {obj}, but got {value}.")
                    else:
                        raise GrabberException(f"Expected a dictionary for property '{property_name}' of {obj}, but got {type(value).__name__}.")
                else:
                    setattr(obj, property_name, value)
            else:
                raise GrabberException("Error occured when accessing attribute " + property_name + " of " + str(obj) + ". Attribute is None.")
        else:
            raise GrabberException(f"Object {obj} has no attribute {property_name}")
        
    @staticmethod
    def set_properties(obj, properties : dict):
        """
        Set multiple properties of an object.
        """
        for property_name, value in properties.items():
            ClassUtils.set_property(obj, property_name, value)
    
    @staticmethod        
    def get_dataclass_fields(clazz : type):
        """
        Get the fields of a dataclass.
        """
        # Get only dataclass fields explicitly defined with field(...)
        dataclass_fields = [
            f for f in fields(clazz)
            if f.default is not MISSING or f.default_factory is not MISSING
        ]
        return dataclass_fields