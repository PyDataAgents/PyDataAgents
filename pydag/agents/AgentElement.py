from __future__ import annotations
import json
import builtins
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid
from loguru import logger


from .AgentElementException import AgentElementException
from .AgentStates import AgentElementState
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
    id : str = field(default_factory=lambda: str(uuid.uuid4()), metadata = {"description": "unique identifier of element in DataAgent application"})
    load_on_install : bool = field(default=False, metadata = {"description": "specifies whether the AgentElement should try to load from local json config file on install"})
      
    def __post_init__(self):
        """
        Initialize the agent element type and state
        """
        self.type = self.__module__ + "." + self.__class__.__name__
        self._state : AgentElementState = AgentElementState.UNINSTALLED
        
    def name(self) -> str:
        s = self.__class__.__name__ + "[" + self.id + "]"
        return s
    
    @classmethod
    def cname(cls) -> str:
        s = cls.__name__
        return s

    def config_options(self, with_descriptions = False) -> dict:
        """ returns a dictionary of the configuration options for the `AgentElement` instance, including descriptions if specified.
        """        
        result : dict = ClassUtils.config_options(self, with_descriptions)
        return result

    @classmethod
    def unique_id(cls):
        """
        Generate a unique ID for the agent element class
        
        Returns:
            str: A unique identifier for the agent element class
        """
        return f"{cls.__name__} [{uuid.uuid4()}]"
    
    @abstractmethod
    def _on_install(self, agent : Agent = None):
        """ installation logic for the element, can be used to reference other agent elements

        Args:
            agent (Agent, optional): _description_. Defaults to None.
        """
    
    @abstractmethod
    def _on_uninstall(self, agent : Agent = None):
        """ uninstallation logic for the element

        Args:
            agent (Agent, optional): _description_. Defaults to None.
        """
    
    def install(self, agent : Agent = None):
        """initializes the element with respect to startup functionality or initial internal object creation,
           if agent is not None, it can be used to reference or create other agent elements
           the method should always be used in child classes with super().install()
        """
        try:
            self._check_state(AgentElementState.INSTALLED)
            if self.load_on_install:
                self.load(agent.save_folder)
            self._on_install(agent)
            self._state = AgentElementState.INSTALLED
        except AgentElementException as e:
            self._state = AgentElementState.ERROR
            raise AgentElementException(f"Could not install {self.__class__.__name__}:\n\t{e.message}") from e
        
    def uninstall(self, agent : Agent = None):
        """resets the element, this method can be used to stop internal element logic or reset objects that were initialized on creation
        """
        self._on_uninstall(agent)
        self._state = AgentElementState.UNINSTALLED
        return
    
    def load(self, from_file : str):
        """ load `AgentElement` config from filesystem
        
        Args:
            from_file (str): path to the file to load the config from
        """
        file = from_file + self.id + ".json"
        if FileUtils.exists_file(file):
            with open(file, "r", encoding="utf-8") as json_file:
                d = json.load(json_file)
                ClassUtils.set_properties(self, d)
        else:
            logger.warning("no configuration file " + self.id + ".json to load from was found")
    
    def save(self, to_file : str):
        """ saves the `AgentElement` config to filesystem
        
        Args:
            to_file (str): path to the file to save the config to
        """
        d = self.config_options()
        with open(to_file + self.id + ".json", "w", encoding="utf-8") as json_file:
            json.dump(d, json_file, indent = 4)  # "indent" makes the output more readable
            
    def get_state(self) -> AgentElementState:
        """
        method to get the current state of the element
        Returns:
            AgentState: current state of the element
        """
        return self._state
    
    def set_state(self, state : AgentElementState):
        """ method to set the `AgentElement`s internal `state`

        Args:
            state (AgentElementState): state enum
        """
        self._state = state
    
    def _check_state(self, next_state : AgentElementState):
        match(next_state):
            case AgentElementState.UNINSTALLED:
                if self._state != AgentElementState.ERROR and self._state != AgentElementState.INSTALLED:
                    raise AgentElementException(f"{self.__class__.__name__} {self.id} cannot be running when uninstalling!")
                
            case AgentElementState.INSTALLED:
                # any prior state is allowed
                return
                
            case AgentElementState.ERROR:
                # any prior state is allowed
                return
            
            case _:
                raise AgentElementException(f"Unknown {AgentElementState.__name__} was found!")
        
    def contains_element(self, id : str) -> bool:
        """ checks whether this `AgentElement` contains another `AgentElement` specified by `id`"""
        seen = {builtins.id(self)}
        stack = list(vars(self).values())
        while stack:
            value = stack.pop()
            if isinstance(value, AgentElement):
                value_obj_id = builtins.id(value)
                if value_obj_id in seen:
                    continue
                if value.id == id:
                    return True
                seen.add(value_obj_id)
                stack.extend(vars(value).values())
            elif isinstance(value, dict):
                stack.extend(value.values())
            elif isinstance(value, (list, tuple, set)):
                stack.extend(value)
        return False
