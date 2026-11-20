import json
from typing import Any

from .FileUtils import FileUtils


def _reject_constant(value: str) -> None:
    raise ValueError("Invalid JSON constant: " + value)


class JsonUtils:
    """ utility class for collection of helpful json methods
    """

    @staticmethod
    def extract_fields(payload: str, keys: list[str]) -> dict[str, Any]:
        """Select required fields from a complete JSON object; raise ValueError on invalid input or missing fields."""
        try:
            parsed = json.loads(payload, parse_constant=_reject_constant)
        except (TypeError, ValueError) as exc:
            raise ValueError("Expected valid JSON text") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Expected a JSON object")
        try:
            return {key: parsed[key] for key in keys}
        except KeyError as exc:
            raise ValueError("Missing required JSON field: " + exc.args[0]) from exc
    
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
