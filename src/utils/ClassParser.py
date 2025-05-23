import importlib


class ClassParser:
    
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
        Clazz = ClassParser.create_class(fully_qualified_class_name)
        return Clazz()
    
    @staticmethod
    def set_property(obj, property_name, value):
        """
        Set a property of an object.
        """
        if hasattr(obj, property_name):
            setattr(obj, property_name, value)
        else:
            raise AttributeError(f"Object {obj} has no attribute {property_name}")
        
    @staticmethod
    def set_properties(obj, properties : dict):
        """
        Set multiple properties of an object.
        """
        for property_name, value in properties.items():
            ClassParser.set_property(obj, property_name, value)