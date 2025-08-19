import json
from ..buffers.Buffer import Buffer
from .Agent import Agent
from .AgentException import AgentException
from ..utils.ClassUtils import ClassUtils


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
    MAPPING = "mapping"
    MAPPINGS = "mappings"
    SERVICE = "service"
    SERVICES = "services"
    
    TYPE = "type"
    ID = "id"
    DESCRIPTION = "description"

    # Buffer Keywords    
    DATA_TYPE = "data_type"
    CAPACITY = "capacity"
    UNIT = "unit"
    INITIAL_VALUES = "initial_values"    
    DATA = "data"
    META = "meta"    
    VALUES = "values"
    TIMESTAMPS = "timestamps"    
    INFINITE_CAPACITY = -1

    def __init__(self, agent : Agent = None):
        self.agent_config = dict()
        self.adapter_configs = []
        self.buffer_configs = []
        self.mapping_configs = []
        self.service_configs = []
        
        if agent is not None:
            # create agent config
            self.agent_config = agent.config_options()
            # create adapter configs
            for adapter in agent.adapter_store.values():
                self.adapter_configs.append(adapter.config_options())       
            # create buffer configs
            for buffer in agent.buffer_store.values():
                self.buffer_configs.append(buffer.config_options())
            # create mapping configs
            for mapping_thread in agent.mapping_store.values():
                self.mapping_configs.append(mapping_thread.mapping.config_options())
            # create service configs
            for service in agent.service_store.values():
                self.service_configs.append(service.config_options())
    
    def create(self) -> Agent:
        """
        Create a agent instance from the configuration.
        """
        if len(self.agent_config) > 0:
            agent : Agent = ClassUtils.create_instance(self.agent_config[AgentConfig.TYPE])            
            ClassUtils.set_properties(agent, self.agent_config)
            if len(self.buffer_configs) > 0:
                for buffer_config in self.buffer_configs:
                    buffer : Buffer = ClassUtils.create_instance(buffer_config[AgentConfig.TYPE])
                    ClassUtils.set_properties(buffer, buffer_config)
                    agent.add_buffer(buffer)
            if len(self.adapter_configs) > 0:
                for adapter_config in self.adapter_configs:
                    adapter = ClassUtils.create_instance(adapter_config[AgentConfig.TYPE])
                    ClassUtils.set_properties(adapter, adapter_config)
                    agent.add_adapter(adapter)
            if len(self.mapping_configs) > 0:
                for mapping_config in self.mapping_configs:
                    mapping = ClassUtils.create_instance(mapping_config[AgentConfig.TYPE])
                    ClassUtils.set_properties(mapping, mapping_config)
                    agent.add_mapping(mapping)
            if len(self.service_configs) > 0:
                for service_config in self.service_configs:
                    service = ClassUtils.create_instance(service_config[AgentConfig.TYPE])
                    ClassUtils.set_properties(service, service_config)
                    agent.add_service(service)
            return agent
        else:
            raise AgentException("agent configuration is not set.")
    
    def to_dict(self) -> dict:
        """
        Convert the configuration to a JSON string.
        """
        d = dict()
        d[AgentConfig.AGENT] = self.agent_config
        d[AgentConfig.ADAPTERS] = self.adapter_configs
        d[AgentConfig.BUFFERS] = self.buffer_configs
        d[AgentConfig.MAPPINGS] = self.mapping_configs
        d[AgentConfig.SERVICES] = self.service_configs    
        return d
     
    def to_json(self) -> str:
        """
        Convert the configuration to a JSON string.
        """                
        return json.dumps(self.to_dict(), indent=4)
               
    def __str__(self) -> str:
        return self.to_json()