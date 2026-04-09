import json
from typing import Any

from .FileUtils import FileUtils


class JsonUtils:
    """ utility class for collection of helpful json methods
    """
    
    @staticmethod
    def read(path : str, encoding : str = "utf-8") -> dict:
        if FileUtils.exists_file(path):
            with open(path, "r", encoding=encoding) as f:
                data = json.load(f)
                return data
        else:
            return None
    
    @staticmethod    
    def write(path : str, data : dict, encoding : str = "utf-8"):
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=4)
            
    @staticmethod
    def replace(path : str, property : str, value : Any, encoding : str = "utf-8") -> bool:
        if FileUtils.exists_file(path):
            data = JsonUtils.read(path, encoding=encoding)
            if property in data:
                data[property] = value
                JsonUtils.write(path, data, encoding=encoding)         
                return True
            else:
                return False
        else:
            return False
