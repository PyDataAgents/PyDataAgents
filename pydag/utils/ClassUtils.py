from __future__ import annotations
from dataclasses import MISSING, fields
import importlib.util
from pathlib import Path
import sys
import inspect

from ..agents.AgentException import AgentException

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
                from ..agents.AgentElement import AgentElement
                if isinstance(attr, AgentElement):
                    if isinstance(value, dict):
                        # If the value is a dictionary, set properties of the AgentElement
                        if "type" in value:
                            # If the dictionary contains a type, create an instance of that type
                            sub_obj = ClassUtils.create_instance(value["type"])
                            ClassUtils.set_properties(sub_obj, value)
                            setattr(obj, property_name, sub_obj)
                        else:
                            raise AgentException(f"Expected a dictionary with 'type' for property '{property_name}' of {obj}, but got {value}.")
                    else:
                        raise AgentException(f"Expected a dictionary for property '{property_name}' of {obj}, but got {type(value).__name__}.")
                else:
                    setattr(obj, property_name, value)
            else:
                raise AgentException("Error occured when accessing attribute " + property_name + " of " + str(obj) + ". Attribute is None.")
        else:
            raise AgentException(f"Object {obj} has no attribute {property_name}")
        
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
    
    @staticmethod
    def get_superclasses(clazz) -> list:
        return [class_.__name__ for class_ in clazz.__mro__]
    
    @staticmethod
    def load_instance(file_path : str, class_name : str, *args, **kwargs) -> object:
        """Load class dynamically from file

        Args:
            file_path (str): name of the *.py file
            class_name (str): name of the class

        Returns:
            object: instance of the specified class
        """
        path = Path(file_path).resolve()
        module_name = path.stem
        # Load module spec
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        # Fetch class by name
        cls = getattr(module, class_name)
        # Instantiate
        return cls(*args, **kwargs)
    

    @staticmethod
    def load_methods(file_path : str) -> dict:
        script_path = Path(file_path).resolve()
        # Load module dynamically
        spec = importlib.util.spec_from_file_location("rules_module", script_path)
        rules_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rules_module)
        # Collect all top-level callables (functions) in the module
        methods = {
            name: func
            for name, func in inspect.getmembers(rules_module, inspect.isfunction)
        }
        return methods