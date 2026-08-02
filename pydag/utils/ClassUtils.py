from __future__ import annotations
import ast
from dataclasses import MISSING, fields, is_dataclass
import importlib.util
from pathlib import Path
import sys
import inspect
from types import FunctionType
from typing import Any, get_type_hints

TYPE_PROPERTY : str = "type" # used to specify the class type of an object in a dictionary/list or other object when setting properties of an object
    
class ClassUtils:
    """ Utility class for working with classes and their instances. """
    
    @staticmethod
    def config_options(obj : Any, with_descriptions = False) -> dict:
        """ creates a dictionary with configuration options of the given object
        `obj` must be a dataclass or an object with dataclass fields. The function will iterate over the fields of the object and extract their values,
        descriptions (if available), and any nested configuration options for fields that are instances of `dataclass`.
        The resulting dictionary will contain the configuration options for the object, including nested configurations for any other
        `dataclass` fields.

        Args:
            obj (Any): _description_
            with_descriptions (bool, optional): _description_. Defaults to False.

        Returns:
            dict: nested config options
        """
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            if is_dataclass(value):
                if with_descriptions:
                    if len(f.metadata) > 0:
                        result[f.name] = {
                            "value": ClassUtils.config_options(value, with_descriptions),
                            "description": f.metadata.get("description", "")
                        }
                    else:
                        result[f.name] = {
                            "value": ClassUtils.config_options(value, with_descriptions),
                            "description": ""
                        }
                else:
                    result[f.name] = ClassUtils.config_options(value, with_descriptions)
            elif isinstance(value, list):
                li = list()
                for item in value:
                    if is_dataclass(item):
                        li.append(ClassUtils.config_options(item, with_descriptions))
                    else:
                        li.append(item)
                if with_descriptions:
                    if len(f.metadata) > 0:
                        result[f.name] = {
                            "value": li,
                            "description": f.metadata.get("description", "")
                        }
                    else:
                        result[f.name] = {
                            "value": li,
                            "description": ""
                        }
                else:
                    result[f.name] = li
            elif isinstance(value, dict):
                d = dict()
                for k, v in value.items():
                    if is_dataclass(v):
                        d[k] = ClassUtils.config_options(v, with_descriptions)
                    else:
                        d[k] = v
                if with_descriptions:
                    if len(f.metadata) > 0:
                        result[f.name] = {
                            "value": d,
                            "description": f.metadata.get("description", "")
                        }
                    else:
                        result[f.name] = {
                            "value": d,
                            "description": ""
                        }
                else:
                    result[f.name] = d
            elif hasattr(value, "__dict__"):
                if with_descriptions:
                    if len(f.metadata) > 0:
                        result[f.name] = {
                            "value": ClassUtils.config_options(value, with_descriptions),
                            "description": f.metadata.get("description", "")
                        }
                    else:
                        result[f.name] = {
                            "value": ClassUtils.config_options(value, with_descriptions),
                            "description": ""
                        }
                else:
                    result[f.name] = ClassUtils.config_options(value, with_descriptions)
            else:
                if with_descriptions:
                    if len(f.metadata) > 0:
                        result[f.name] = {
                                "value": value,
                                "description": f.metadata.get("description", "")
                            }
                    else:
                        result[f.name] = {
                            "value": value,
                            "description": ""
                        }
                else:
                    result[f.name] = value
        return result
    
    @staticmethod
    def create_class(fully_qualified_class_name : str):
        """
        Create a class from the class name.
        """
        # check if module name is also a class name, if so load the module and get the class from it
        try:
            module = importlib.import_module(fully_qualified_class_name)
            class_name = fully_qualified_class_name.rsplit(".", 1)[-1]
            if hasattr(module, class_name):
                clazz = getattr(module, fully_qualified_class_name.rsplit(".", 1))
                return clazz
        except ModuleNotFoundError:
            # Split the fully qualified class name into module and class name
            module_name, class_name = fully_qualified_class_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            # Check if the module has the specified class
            if hasattr(module, class_name):
                clazz = getattr(module, class_name)
                return clazz
            else:
                return None
        
        
    
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
            if attr is None:
                if property_name in obj.__annotations__:
                    attr = obj.__annotations__[property_name]
            #print(type(attr))
            if is_dataclass(attr):
                if isinstance(value, dict):
                    # If the value is a dictionary, set properties of the dataclass
                    if TYPE_PROPERTY in value:
                        # If the dictionary contains a type, create an instance of that type
                        sub_obj = ClassUtils.create_instance(value[TYPE_PROPERTY])
                        # remove the type property from the dictionary before setting properties
                        if not hasattr(sub_obj, TYPE_PROPERTY):
                            value.pop(TYPE_PROPERTY, None)  
                        ClassUtils.set_properties(sub_obj, value)
                        setattr(obj, property_name, sub_obj)
                    else:
                        if isinstance(attr.__class__, type):
                            try:
                                clazz = type(attr)                                                        
                                sub_obj = clazz()
                                ClassUtils.set_properties(sub_obj, value)
                                setattr(obj, property_name, sub_obj)
                            except TypeError as e:
                                raise ValueError(f"Error occurred while creating instance of '{property_name}'") from e
                        else:
                            raise ValueError(f"Expected a class object for '{property_name}'.")
                else:
                    raise ValueError(f"Expected a dictionary for property '{property_name}' of {obj}, but got {type(value).__name__}.")
            elif isinstance(attr, dict):
                if isinstance(value, dict):
                    if len(value) > 0:
                        key = next(iter(value))
                        if isinstance(value[key], dict):
                            if TYPE_PROPERTY in value[key]:
                                element_dic = {}
                                for k, v in value.items():
                                    sub_obj = ClassUtils.create_instance(v[TYPE_PROPERTY])
                                    if not hasattr(sub_obj, TYPE_PROPERTY):
                                        v.pop(TYPE_PROPERTY, None)
                                    ClassUtils.set_properties(sub_obj, v)
                                    element_dic[k] = sub_obj
                                setattr(obj, property_name, element_dic)
                            else:
                                raise ValueError(f"No '{TYPE_PROPERTY}' property was specified in dict of object properties {value} for property '{property_name}' of {obj}")
                        else:
                            # just set the content of the dictionary, this should only be content, that can be serialized
                            setattr(obj, property_name, value)
                else:
                    raise ValueError(f"Expected a dictionary for property '{property_name}' of {obj}")
            elif isinstance(attr, list):
                if isinstance(value, list):
                    if len(value) > 0:
                        if isinstance(value[0], dict):
                            if TYPE_PROPERTY in value[0]:
                                element_list = []
                                for item in value:
                                    sub_obj = ClassUtils.create_instance(item[TYPE_PROPERTY])
                                    # remove the type property from the dictionary before setting properties
                                    if not hasattr(sub_obj, TYPE_PROPERTY):
                                        item.pop(TYPE_PROPERTY, None)
                                    ClassUtils.set_properties(sub_obj, item)
                                    element_list.append(sub_obj)
                                setattr(obj, property_name, element_list)
                            else:
                                raise ValueError(f"No '{TYPE_PROPERTY}' property was specified in list of object properties {value} for property '{property_name}' of {obj}")    
                        else:
                            # just set the content of the list, this should only be content, that can be serialized
                            setattr(obj, property_name, value)
                else:
                    raise ValueError(f"Expected a list for property '{property_name}' of {obj}")
            elif isinstance(attr, type):
                if is_dataclass(attr):
                    if isinstance(value, dict):
                        # If the value is a dictionary, set properties of the dataclass
                        if TYPE_PROPERTY in value:
                            # If the dictionary contains a type, create an instance of that type
                            sub_obj = ClassUtils.create_instance(value[TYPE_PROPERTY])
                            # remove the type property from the dictionary before setting properties
                            if not hasattr(sub_obj, TYPE_PROPERTY):
                                value.pop(TYPE_PROPERTY, None)
                            ClassUtils.set_properties(sub_obj, value)
                            setattr(obj, property_name, sub_obj)
                        else:
                            raise ValueError(f"Expected a dictionary with '{TYPE_PROPERTY}' for property '{property_name}' of {obj}, but got {value}.")
                    else:
                        raise ValueError(f"Expected a dictionary for property '{property_name}' of {obj}, but got {type(value).__name__}.")
                else:
                    # check if property is an int
                    current_value = getattr(obj, property_name)
                    if isinstance(current_value, int) and not isinstance(current_value, bool):
                        setattr(obj, property_name, int(value))
                    elif isinstance(current_value, bool):
                        setattr(obj, property_name, bool(value))
                    else:
                        setattr(obj, property_name, value)
            else:
                # check if property is an int
                current_value = getattr(obj, property_name)
                if isinstance(current_value, int) and not isinstance(current_value, bool):
                    setattr(obj, property_name, int(value))
                elif isinstance(current_value, bool):
                    setattr(obj, property_name, bool(value))
                else:
                    setattr(obj, property_name, value)
        else:
            raise ValueError(f"Object {obj} has no attribute {property_name}")
        
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
    def load_class(file_path : str, class_name : str) -> type:
        """Load class dynamically from file

        Args:
            file_path (str): name of the *.py file
            class_name (str): name of the class

        Returns:
            object: the specified class type
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
        return cls

    @staticmethod
    def load_instance(file_path : str, class_name : str, *args, **kwargs) -> object:
        """Load class instance dynamically from file

        Args:
            file_path (str): name of the *.py file
            class_name (str): name of the class
            *args (Any): constructor arguments
            **kwargs (Dict): dictionary of constructor arguments

        Returns:
            object: instance of the specified class
        """
        # Fetch class by name
        cls = ClassUtils.load_class(file_path=file_path, class_name = class_name)
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
    
    @staticmethod
    def get_subclasses(cls, ignore_abstract : bool = False) -> set:
        """ returns all subclasses of type `cls` recursively
            and returns them as set
        """
        subclasses = cls.__subclasses__()
        names = set()
        for sub in subclasses:
            #print(sub.__qualname__)
            if inspect.isabstract(sub) and ignore_abstract:
                # do nothing
                pass
            else:
                names.update({f"{sub.__module__}"})
            names.update(ClassUtils.get_subclasses(sub, ignore_abstract))
        return names
    
    @staticmethod
    def find_subclasses(clazz : type, folder : str) -> tuple[str, str]:
        sub_clazzes : list[str] = []
        file_paths : list[str] = []
        for file in Path(folder).rglob('*.py'):
            try:
                tree = ast.parse(file.read_text(encoding='utf-8'))
                for node in list(ast.walk(tree)):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == clazz.__name__:
                                file_paths.append(str(file))
                                sub_clazzes.append(node.name)
                            elif isinstance(base, ast.Attribute) and base.attr == clazz.__name__:
                                file_paths.append(str(file))
                                sub_clazzes.append(node.name)
            except Exception:
                continue  # skip invalid Python files

        return tuple(zip(file_paths, sub_clazzes))