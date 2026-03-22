from dataclasses import fields
import json
import os
from typing import TYPE_CHECKING, Any


from .AgentElement import AgentElement
from .AgentException import AgentException
from ..utils.ClassUtils import ClassUtils

if TYPE_CHECKING:    
    from .Agent import Agent

class AgentConfig:
    """
    Configuration class for the agent application.
    """
          
    # Agent Keywords   
    AGENT = "agent"
    BUFFER = "buffer"
    BUFFERS = "buffers"
    ADAPTER = "adapter"
    ADAPTERS = "adapters"
    SERVICE = "service"
    SERVICES = "services"
    
    TYPE = "type"
    ID = "id"
    DESCRIPTION = "description"
    
    # Adapter Keywords    
    ADDRESS = "address"
    ADDRESSES = "addresses"
    

    # Buffer Keywords    
    DATA_TYPE = "data_type"
    CAPACITY = "capacity"
    UNIT = "unit"
    INITIAL_VALUES = "initial_values"    
    DATA = "data"
    META = "meta"    
    VALUES = "values"
    TIMESTAMPS = "timestamps"   
    INDEX = "index" 
    INFINITE_CAPACITY = -1  
    
    # Node Config Keywords  
    FEATURE = "feature"
    FEATURES = "features"
    Y_HAT = "y_hat"
    
    # Service Config Keywords
    MAX_EXPONENTIAL_SECONDS = 60 * 60 * 24 * 7


    # resource folder
    RESOURCE_FOLDER = "." + os.sep + "resources"  + os.sep
    MODEL_RESOURCE_FOLDER = RESOURCE_FOLDER + "models" + os.sep
    EMBEDDINGS_RESOURCE_FOLDER = RESOURCE_FOLDER + "embeddings" + os.sep
    SAVE_FOLDER = RESOURCE_FOLDER + "save" + os.sep

    @staticmethod
    def config_options(obj : Any, with_descriptions = False) -> dict:
        """ creates a dictionary with configuration options of the given object

        Args:
            obj (Any): _description_
            with_descriptions (bool, optional): _description_. Defaults to False.

        Returns:
            dict: _description_
        """
        result = {}
        for f in fields(obj):
            # check for fields with metadata only
            if len(f.metadata) > 0:
                value = getattr(obj, f.name)
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
    
    def __init__(self, agent : 'Agent' = None):
        self._agent_config : dict = None
        if agent:
            self._agent_config = AgentConfig.config_options(agent)    
            
    def create(self) -> 'Agent':
        """
        Create a agent instance from the configuration.
        """
        if len(self._agent_config) > 0:
            from .Agent import Agent
            agent : Agent = ClassUtils.create_instance(Agent.__module__)
            ClassUtils.set_properties(agent, self._agent_config)
            return agent
        else:
            raise AgentException("agent configuration is not set.")
    
    def to_dict(self) -> dict:
        """
        Convert the configuration to a dictionary
        """
        return self._agent_config
    
    @staticmethod
    def from_dict(d : dict) -> 'AgentConfig':
        """
        Load the configuration from a dictionary.
        """
        ac = AgentConfig()
        ac._agent_config = d
        return ac
         
    def to_json(self) -> str:
        """
        Convert the configuration to a JSON string.
        """                
        return json.dumps(self.to_dict(), indent=4)
               
    def __str__(self) -> str:
        return self.to_json()