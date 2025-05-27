from abc import ABC
from dataclasses import dataclass, field, fields
import uuid
from loguru import logger

@dataclass
class GrabberElement(ABC):
    """
    Abstract base class for grabber elements.
    """

    type : str = field(default=None, metadata={"description": "fully qualified package and class name descriptor"})
    id : str = field(default=None, metadata = {"description": "unique identifier of element in DataGrabber application"})
    
    LOGGER = logger
    
    def __init__(self, id : str = None):
        """
        Initialize the grabber element and assign a unique ID.
        """
        self.type = self.__module__
        if id is None:            
            self.id = self.unique_id()
        else:
            self.id = id       
        
    def name(self) -> str:
        s = self.__class__.__name__ + "[" + self.id + "]"
        return s
    
    @classmethod
    def cname(cls) -> str:
        s = cls.__name__
        return s

    def config_options(self, with_descriptions = False) -> dict:
        result = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if with_descriptions:
                result[f.name] = {
                    "value": value,
                    "description": f.metadata.get("description", "")
                }
            else:
                if isinstance(value, GrabberElement):
                    result[f.name] = value.config_options(with_descriptions)
                elif isinstance(value, list):
                    li = list()
                    for item in value:
                        if isinstance(item, GrabberElement):
                            li.append(item.config_options())
                        else:
                            li.append(item)
                    result[f.name] = li
                elif isinstance(value, dict):
                    d = dict()
                    for k, v in value.items():
                        if isinstance(v, GrabberElement):
                            d[k] = v.config_options()
                        else:
                            d[k] = v
                    result[f.name] = d
                else:
                    result[f.name] = value
        return result

    def unique_id(self):
        """
        Generate a unique ID for the grabber element class
        
        Returns:
            str: A unique identifier for the grabber element class
        """
        return f"{self.__class__.__name__} [{uuid.uuid4()}]"