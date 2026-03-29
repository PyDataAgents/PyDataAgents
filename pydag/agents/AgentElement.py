from __future__ import annotations
import json
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid
from loguru import logger


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
        self.type = self.__module__
        self._state : AgentElementState = AgentElementState.UNINSTALLED
        
    def name(self) -> str:
        s = self.__class__.__name__ + "[" + self.id + "]"
        return s
    
    @classmethod
    def cname(cls) -> str:
        s = cls.__name__
        return s

    def config_options(self, with_descriptions = False) -> dict:
        from .AgentConfig import AgentConfig
        result = AgentConfig.config_options(self, with_descriptions)
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
        if self.load_on_install:
            self.load()
        self._on_install(agent)
        self._state = AgentElementState.INSTALLED
        
    def uninstall(self, agent : Agent = None):
        """resets the element, this method can be used to stop internal element logic or reset objects that were initialized on creation
        """
        self._on_uninstall(agent)
        self._state = AgentElementState.UNINSTALLED
        return
    
    def load(self):
        """ load `AgentElement` config from filesystem
        """
        from .AgentConfig import AgentConfig
        file = AgentConfig.SAVE_FOLDER + self.id + ".json"
        if FileUtils.exists_file(file):
            with open(file, "r", encoding="utf-8") as json_file:
                d = json.load(json_file)
                ClassUtils.set_properties(self, d)
        else:
            logger.warning("no configuration file " + self.id + ".json to load from was found")
    
    def save(self):
        """ saves the `AgentElement` config to filesystem
        """
        from .AgentConfig import AgentConfig
        d = self.config_options()
        with open(AgentConfig.SAVE_FOLDER + self.id + ".json", "w", encoding="utf-8") as json_file:
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