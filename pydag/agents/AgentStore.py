from dataclasses import dataclass, field
from threading import Lock

from .YAMLConfig import YAMLConfig
from .AgentConfig import AgentConfig
from ..utils.FileUtils import FileUtils
from .Agent import Agent

@dataclass
class AgentStore:
    """A store for managing template based agents, that users can create in a multi-client setup."""
    
    template_paths : list[str] = field(default_factory=list, metadata={"description": "List of paths to agent templates"})
    
    def __post_init__(self):
        self._user_agents : dict[str, list[str]] = dict()
        self._agents : dict[str, Agent] = dict()
        self._templates : dict[str, Agent] = dict()
        self._lock : Lock = Lock()
                
    def load_templates(self):
        with self._lock:
            for path in self.template_paths:
                if FileUtils.exists_folder(path):
                    for file in FileUtils.list_files(path, extension=[".yaml", ".yml"]):
                        config = YAMLConfig(file).load()
                        agent = config.create()
                        self._templates[agent.id] = agent
    
    def add_template(self, agent : Agent):
        with self._lock:
            self._templates[agent.id] = agent

    def add_user(self, user_id : str):
        with self._lock:
            if user_id not in self._user_agents:
                self._user_agents[user_id] = []
    
    def add_agent(self, user_id : str, agent : Agent):
        with self._lock:
            if user_id in self._user_agents:
                self._user_agents[user_id].append(agent.id)
            self._agents[agent.id] = agent
            
    def get_agent(self, user_id : str, agent_id : str) -> Agent:
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                return self._agents[agent_id]
            else:
                return None
        
    def get_templates(self) -> tuple[str, str]:
        with self._lock:
            return [(agent.id, agent.description) for agent in self._templates.values()]
            
    def get_users(self) -> list[str]:
        with self._lock:
            return list(self._user_agents.keys())
        
    def get_user_agents(self, user : str) -> list[Agent]:
        with self._lock:
            if user in self._user_agents:
                return [self._agents[agent_id] for agent_id in self._user_agents[user]]
            else:
                return []
    
    def release_agent(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                self._agents[agent_id].release(blocking=False)

    def terminate_agent(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                self._agents[agent_id].terminate()
                
    
