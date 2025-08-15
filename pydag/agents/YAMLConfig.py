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
        grabber_config = AgentConfig()
        grabber_config.agent_config = d[AgentConfig.AGENT]
        grabber_config.adapter_configs = d[AgentConfig.ADAPTERS]
        grabber_config.buffer_configs = d[AgentConfig.BUFFERS]
        grabber_config.mapping_configs = d[AgentConfig.MAPPINGS]
        grabber_config.service_configs = d[AgentConfig.SERVICES]
        return grabber_config
    
    def save(self, grabber_config: AgentConfig):
        d = dict()
        d[AgentConfig.AGENT] = grabber_config.agent_config
        d[AgentConfig.ADAPTERS] = grabber_config.adapter_configs
        d[AgentConfig.BUFFERS] = grabber_config.buffer_configs
        d[AgentConfig.MAPPINGS] = grabber_config.mapping_configs
        d[AgentConfig.SERVICES] = grabber_config.service_configs
        # make sure the directory exists        
        FileUtils.create_dir(FileUtils.parent_folder(self.file_path))
        yaml_file = open(self.file_path, "w")
        yaml.dump(d, yaml_file, sort_keys=False)
        yaml_file.close()