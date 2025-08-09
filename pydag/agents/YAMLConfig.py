import yaml
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
        grabber_config.grabber_config = d["agent"]
        grabber_config.adapter_configs = d["adapters"]
        grabber_config.buffer_configs = d["buffers"]
        grabber_config.mapping_configs = d["mappings"]
        grabber_config.service_configs = d["services"]
        return grabber_config
    
    def save(self, grabber_config: AgentConfig):
        d = dict()
        d["agent"] = grabber_config.grabber_config
        d["adapters"] = grabber_config.adapter_configs
        d["buffers"] = grabber_config.buffer_configs
        d["mappings"] = grabber_config.mapping_configs
        d["services"] = grabber_config.service_configs
        yaml_file = open(self.file_path, "w")
        yaml.dump(d, yaml_file, sort_keys=False)
        yaml_file.close()