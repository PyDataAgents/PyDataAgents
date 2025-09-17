import yaml

from ..utils.FileUtils import FileUtils
from .FileConfig import FileConfig
from .AgentConfig import AgentConfig


class YAMLConfig(FileConfig):
    """
    YAML configuration class for loading and saving configurations.
    """

    def __init__(self, file_path: str):
        """
        Initialize the YAML configuration with the file path.
        """
        super().__init__(file_path)
    
    def load(self) -> AgentConfig:
        yaml_file = open(self.file_path, "r")
        d = yaml.safe_load(yaml_file)
        yaml_file.close()
        agent_config = AgentConfig()
        agent_config.agent_config = d[AgentConfig.AGENT]
        agent_config.adapter_configs = d[AgentConfig.ADAPTERS]
        agent_config.buffer_configs = d[AgentConfig.BUFFERS]
        agent_config.mapping_configs = d[AgentConfig.MAPPINGS]
        agent_config.service_configs = d[AgentConfig.SERVICES]
        return agent_config
    
    def save(self, agent_config: AgentConfig):
        d = dict()
        d[AgentConfig.AGENT] = agent_config.agent_config
        d[AgentConfig.ADAPTERS] = agent_config.adapter_configs
        d[AgentConfig.BUFFERS] = agent_config.buffer_configs
        d[AgentConfig.MAPPINGS] = agent_config.mapping_configs
        d[AgentConfig.SERVICES] = agent_config.service_configs
        # make sure the directory exists        
        FileUtils.create_dir(FileUtils.parent_folder(self.file_path))
        yaml_file = open(self.file_path, "w")
        yaml.dump(d, yaml_file, sort_keys=False)
        yaml_file.close()