import yaml

from ..utils.FileUtils import FileUtils
from .FileConfig import FileConfig
from .AgentConfig import AgentConfig


class YAMLConfig(FileConfig):
    """
    YAML configuration class for loading and saving configurations.
    """
    
    def load(self) -> AgentConfig:
        yaml_file = open(self._file_path, "r", encoding='utf-8')
        d = yaml.safe_load(yaml_file)
        yaml_file.close()
        agent_config = AgentConfig.from_dict(d)
        return agent_config
    
    def save(self, agent_config: AgentConfig):
        d = agent_config.to_dict()
        # make sure the directory exists when a parent folder is part of the path
        parent_folder = FileUtils.parent_folder(self._file_path)
        if parent_folder:
            FileUtils.create_dir(parent_folder)
        yaml_file = open(self._file_path, "w", encoding='utf-8')
        yaml.dump(d, yaml_file, sort_keys=False)
        yaml_file.close()
