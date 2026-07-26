from __future__ import annotations
from dataclasses import dataclass, field
from multiprocessing import Process
from threading import Lock
from typing import Any
import uuid
from loguru import logger

from .app.AgentApp import AgentApp
from .AgentException import AgentException
from .YAMLConfig import YAMLConfig
from .AgentConfig import AgentConfig
from ..utils.FileUtils import FileUtils
from .Agent import Agent

@dataclass
class AgentStore:
    """A store for managing template based agents, that users can create in a multi-client setup."""
    
    template_paths : list[str] = field(default_factory=list, metadata={"description": "List of paths to agent templates"})
    
    def __post_init__(self):
        self._user_agents : dict[str, set[str]] = dict()
        self._agents_apps : dict[str, AgentApp] = dict()
        self._templates : dict[str, dict] = dict()
        self._agent_processes : dict[str, Process] = dict()
        self._lock : Lock = Lock()
    
    def open(self):
        """ Start the agent store UI Server. This will block the current thread until the server is stopped. """        
        self.load_templates()
                        
    def load_templates(self):
        with self._lock:
            for path in self.template_paths:
                if FileUtils.exists_folder(path):
                    for file in FileUtils.list_files(path, extension=[".yaml", ".yml"]):
                        config = YAMLConfig(file).load()
                        d = config.to_dict()
                        if "id" in d:
                            id = d["id"]                        
                            self._templates[id] = config
                        else:
                            logger.warning(f"Template file {file} does not contain an 'id' field. Skipping.")                     
    
    def add_template(self, agent : Agent):
        with self._lock:
            config = AgentConfig(agent)
            self._templates[agent.id] = config

    def add_user(self, user_id : str):
        with self._lock:
            if user_id not in self._user_agents:
                self._user_agents[user_id] = set()
    
    def add_agent(self, user_id : str, agent_app : AgentApp):
        with self._lock:
            if user_id in self._user_agents:
                self._user_agents[user_id].add(agent_app.get_agent().id)
            else:
                self._user_agents[user_id] = {agent_app.get_agent().id}
            self._agents_apps[agent_app.get_agent().id] = agent_app
            
    def add_agent_from_template(self, user_id : str, template_id : str):
        with self._lock:
            if template_id in self._templates:
                agent_config = self._templates[template_id]
                new_agent = agent_config.create()
                new_agent.id = str(uuid.uuid4())
                self._agents_apps[new_agent.id] = new_agent
                if user_id in self._user_agents:
                    self._user_agents[user_id].add(new_agent.id)
                else:
                    self._user_agents[user_id] = {new_agent.id}
            else:
                raise AgentException(f"Template with ID {template_id} not found.")
            
    def get_agent(self, user_id : str, agent_id : str) -> AgentApp:
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                return self._agents_apps[agent_id]
            else:
                return None
        
    def get_templates(self) -> dict[str, dict]:
        with self._lock:
            return self._templates
            
    def get_users(self) -> list[str]:
        with self._lock:
            return list(self._user_agents.keys())
        
    def get_user_agents(self, user : str) -> list[AgentApp]:
        with self._lock:
            if user in self._user_agents:
                return [self._agents_apps[agent_id] for agent_id in self._user_agents[user]]
            else:
                return []
    
    def release_agent(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                self._agents_apps[agent_id].release(blocking=False)

    def terminate_agent(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                self._agents_apps[agent_id].terminate()
                
    def configure_agent(self, user_id : str, agent_id : str, config : dict[str, Any]):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                agent : Agent = self._agents_apps[agent_id]
                if agent.is_running():
                    raise AgentException(f"{Agent.__name__} with id={agent_id} cannot be configured, while it's running.")
                else:
                    pass            

    def remove_agent(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                agent : Agent = self._agents_apps[agent_id]
                if agent.is_running():
                    raise AgentException(f"{Agent.__name__} with id={agent_id} cannot be removed, when it's running.")
                else:
                    self._agents_apps.pop(agent_id)
                    self._user_agents[user_id].remove(agent_id)
    
    
    
