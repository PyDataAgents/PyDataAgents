from __future__ import annotations
from dataclasses import MISSING, fields
import importlib.util
from pathlib import Path
import sys
import inspect
from types import FunctionType
from typing import get_type_hints

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
        from pydag.agents.AgentConfig import AgentConfig
        if hasattr(obj, property_name):
            attr = getattr(obj, property_name)            
            #print(type(attr))
            from ..agents.AgentElement import AgentElement
            if isinstance(attr, AgentElement):
                if isinstance(value, dict):
                    # If the value is a dictionary, set properties of the AgentElement
                    if AgentConfig.TYPE in value:
                        # If the dictionary contains a type, create an instance of that type
                        sub_obj = ClassUtils.create_instance(value[AgentConfig.TYPE])
                        ClassUtils.set_properties(sub_obj, value)
                        setattr(obj, property_name, sub_obj)
                    else:
                        raise AgentException(f"Expected a dictionary with '{AgentConfig.TYPE}' for property '{property_name}' of {obj}, but got {value}.")
                else:
                    raise AgentException(f"Expected a dictionary for property '{property_name}' of {obj}, but got {type(value).__name__}.")
            elif isinstance(attr, dict):
                if isinstance(value, dict):
                    key = next(iter(value))
                    if isinstance(value[key], dict):
                        if AgentConfig.TYPE in value[key]:
                            element_dic = {}
                            for k, v in value:
                                sub_obj = ClassUtils.create_instance(v[AgentConfig.TYPE])
                                ClassUtils.set_properties(sub_obj, v)
                                element_dic[k] = sub_obj
                            setattr(obj, property_name, element_dic)
                        else:
                            raise AgentException(f"No '{AgentConfig.TYPE}' property was specified in dict of object properties {value} for property '{property_name}' of {obj}")
                    else:
                        # just set the content of the dictionary, this should only be content, that can be serialized
                        setattr(obj, property_name, value)
                else:
                    raise AgentException(f"Expected a dictionary for property '{property_name}' of {obj}")
            elif isinstance(attr, list):
                if isinstance(value, list):
                    if isinstance(value[0], dict):
                        if AgentConfig.TYPE in value[0]:
                            element_list = []
                            for item in value:
                                sub_obj = ClassUtils.create_instance(item[AgentConfig.TYPE])
                                ClassUtils.set_properties(sub_obj, item)
                                element_list.append(sub_obj)
                            setattr(obj, property_name, element_list)
                        else:
                            raise AgentException(f"No '{AgentConfig.TYPE}' property was specified in list of object properties {value} for property '{property_name}' of {obj}")    
                    else:
                        # just set the content of the list, this should only be content, that can be serialized
                        setattr(obj, property_name, value)
                else:
                    raise AgentException(f"Expected a list for property '{property_name}' of {obj}")
            else:
                setattr(obj, property_name, value)
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
    def is_property_list(obj, property) -> bool:
        hints = get_type_hints(obj)
        t = hints.get(property)
        if not t:
            return False
        origin = getattr(t, '__origin__', t)
        if origin == list:
            return True
        else:
            return False
    
    @staticmethod
    def is_property_dict(obj, property) -> bool:
        hints = get_type_hints(obj)
        t = hints.get(property)
        if not t:
            return False
        origin = getattr(t, '__origin__', t)
        if origin == dict:
            return True
        else:
            return False    
    
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
        methods = {}
        
        for name, func in inspect.getmembers(rules_module, inspect.isfunction):
            if name == "dataclass" or name == "field":
                continue  # ignore dataclass methods
            else:
                methods[name] = func        
        
        # Step 2: Find classes and extract their methods
        for _, cls in inspect.getmembers(rules_module, inspect.isclass):
            if cls.__module__ != rules_module.__name__:
                continue  # skip imported classes

            # cls.__dict__ contains only what's defined in the class itself
            for attr_name, attr_value in cls.__dict__.items():
                if attr_name.startswith("__"):
                    continue  # ignore dunder methods like __init__, __repr__, etc.
                if attr_name == "dataclass" or attr_name == "field":
                    continue  # ignore dataclass methods
                if isinstance(attr_value, (FunctionType, classmethod, staticmethod)):
                    # Unwrap staticmethod/classmethod if needed
                    if isinstance(attr_value, (classmethod, staticmethod)):
                        func = attr_value.__func__
                    else:
                        func = attr_value
                    qualified_name = f"{cls.__name__}.{attr_name}"
                    methods[qualified_name] = func
        
        return methods