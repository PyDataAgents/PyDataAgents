from __future__ import annotations
import json
from typing import TYPE_CHECKING
from abc import ABC
from dataclasses import dataclass, field, fields
import uuid
from loguru import logger

from ..utils.ClassUtils import ClassUtils
from ..utils.FileUtils import FileUtils

if TYPE_CHECKING:
    from .Agent import Agent
    
@dataclass
class AgentElement(ABC):
    """
    Abstract base class for agent elements.
    """

    type : str = field(default=None, metadata={"description": "fully qualified package and class name descriptor"})
    id : str = field(default=None, metadata = {"description": "unique identifier of element in DataGrabber application"})
    load_on_install : bool = field(default=False, metadata = {"description": "specifies whether the GrabberElement should try to load from local json config file on install"})
    
        
    def __post_init__(self):
        """
        Initialize the agent element and assign a unique ID.
        """
        self.type = self.__module__                   
        if self.id is None: 
            self.id = self.unique_id()       
        
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
            # check for fields with metadata only
            if len(f.metadata) > 0:
                value = getattr(self, f.name)
                if with_descriptions:
                    result[f.name] = {
                        "value": value,
                        "description": f.metadata.get("description", "")
                    }
                else:
                    if isinstance(value, AgentElement):
                        result[f.name] = value.config_options(with_descriptions)
                    elif isinstance(value, list):
                        li = list()
                        for item in value:
                            if isinstance(item, AgentElement):
                                li.append(item.config_options())
                            else:
                                li.append(item)
                        result[f.name] = li
                    elif isinstance(value, dict):
                        d = dict()
                        for k, v in value.items():
                            if isinstance(v, AgentElement):
                                d[k] = v.config_options()
                            else:
                                d[k] = v
                        result[f.name] = d
                    else:
                        result[f.name] = value
        return result

    @classmethod
    def unique_id(cls):
        """
        Generate a unique ID for the agent element class
        
        Returns:
            str: A unique identifier for the agent element class
        """
        return f"{cls.__name__} [{uuid.uuid4()}]"
    
    def install(self, agent : Agent = None):
        """initializes the element with respect to startup functionality or initial internal object creation,
           if agent is not None, it can be used to reference or create other agent elements
           the method should always be used in child classes with super().install()
        """
        if self.load_on_install:
            self.load()

        
    def deinstall(self, agent : Agent = None):
        """resets the element, this method can be used to stop internal element logic or reset objects that were initialized on creation
        """
        return
    
    def load(self):
        file = self.id + ".json"
        if FileUtils.exists_file(file):
            with open(file, "r") as json_file:
                d = json.load(json_file)
                ClassUtils.set_properties(self, d)
        else:
            logger.warning("no configuration file " + self.id + ".json to load from was found")
    
    def save(self):
        # Write config options to JSON file
        d = self.config_options()
        with open(self.id + ".json", "w") as json_file:
            json.dump(d, json_file, indent = 4)  # "indent" makes the output more readable