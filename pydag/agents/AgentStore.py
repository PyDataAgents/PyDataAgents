from __future__ import annotations
from dataclasses import dataclass, field
import multiprocessing
from threading import Lock
from typing import Any
import uuid
from loguru import logger

from .app.AgentApp import AgentApp
from .AgentException import AgentException
from .AgentKeywords import AgentKeywords
from ..utils.FileUtils import FileUtils
from .Agent import Agent

def _run_app_process(app_config: dict) -> None:
    aa : AgentApp = AgentApp.load(app_config)
    aa.create()
    aa.run()

@dataclass
class AgentStore:
    """A store for managing template based agents, that users can create in a multi-client setup."""
    
    template_paths : list[str] = field(default_factory=list, metadata={"description": "List of paths to agent templates"})
    
    def __post_init__(self):
        self._user_apps : dict[str, set[str]] = dict()
        self._agents_apps : dict[str, AgentApp] = dict()
        self._templates : dict[str, dict] = dict()
        self._processes: dict[str, multiprocessing.Process] = {}
        self._lock : Lock = Lock()
    
    def open(self):
        """ Start the agent store UI Server. This will block the current thread until the server is stopped. """        
        self.load_templates()
                        
    def load_templates(self):
        with self._lock:
            for path in self.template_paths:
                if FileUtils.exists_folder(path):
                    for file in FileUtils.list_files(path, extension=[".yaml", ".yml"]):
                        aa : AgentApp = AgentApp.load(file)
                        config = aa.config_options()
                        if AgentKeywords.ID in config[AgentKeywords.AGENT]:
                            id = config[AgentKeywords.AGENT][AgentKeywords.ID]
                            self._templates[id] = config
                        else:
                            logger.warning(f"Template file {file} does not contain an 'id' field. Skipping.")                     
    
    def add_template_from(self, agent_app : AgentApp):
        with self._lock:
            config = agent_app.config_options()
            if AgentKeywords.ID in config[AgentKeywords.AGENT]:
                id = config[AgentKeywords.AGENT][AgentKeywords.ID]
                self._templates[id] = config

    def add_template(self, app_config : dict):
        with self._lock:
            if AgentKeywords.ID in app_config[AgentKeywords.AGENT]:
                id = app_config[AgentKeywords.AGENT][AgentKeywords.ID]
                self._templates[id] = app_config
            else:
                raise AgentException(f"Template config does not contain an 'id' field. Cannot add template.")
    
    def add_user(self, user_id : str):
        with self._lock:
            if user_id not in self._user_apps:
                self._user_apps[user_id] = set()
    
    def add_app(self, user_id : str, agent_app : AgentApp):
        with self._lock:
            if user_id in self._user_apps:
                self._user_apps[user_id].add(agent_app.get_agent().id)
            else:
                self._user_apps[user_id] = {agent_app.get_agent().id}
            self._agents_apps[agent_app.get_agent().id] = agent_app
            
    def add_agent_from_template(self, user_id : str, template_id : str):
        with self._lock:
            if template_id in self._templates:
                app_config = self._templates[template_id]
                new_agent_app = AgentApp.load(app_config)
                new_agent_app.get_agent().id = str(uuid.uuid4())
                self._agents_apps[new_agent_app.get_agent().id] = new_agent_app
                if user_id in self._user_apps:
                    self._user_apps[user_id].add(new_agent_app.get_agent().id)
                else:
                    self._user_apps[user_id] = {new_agent_app.get_agent().id}
            else:
                raise AgentException(f"Template with ID {template_id} not found.")
            
    def get_agent(self, user_id : str, agent_id : str) -> AgentApp:
        with self._lock:
            if user_id in self._user_apps and agent_id in self._user_apps[user_id]:
                return self._agents_apps[agent_id]
            else:
                return None
        
    def get_templates(self) -> dict[str, dict]:
        with self._lock:
            return self._templates
            
    def get_users(self) -> list[str]:
        with self._lock:
            return list(self._user_apps.keys())
        
    def get_user_apps(self, user : str) -> list[AgentApp]:
        with self._lock:
            if user in self._user_apps:
                return [self._agents_apps[agent_id] for agent_id in self._user_apps[user]]
            else:
                return []
    
    def run_app(self, agent_id: str) -> multiprocessing.Process:
        if agent_id not in self._agents_apps:
            raise KeyError(f"No {AgentApp.__name__} with id={agent_id} was registered")

        existing_process = self._processes.get(agent_id)
        if existing_process is not None and existing_process.is_alive():
            return existing_process

        app_config = self._agents_apps[agent_id].config_options()
        context = multiprocessing.get_context("spawn")
        process = context.Process(target=_run_app_process, args=(app_config,), daemon=True)
        process.start()
        self._processes[agent_id] = process
        return process
    
    def shutdown_app(self, agent_id: str) -> None:
        process = self._processes.get(agent_id)
        if process is None:
            return

        if process.is_alive():
            process.terminate()
            process.join(timeout=5)

        self._processes.pop(agent_id, None)
                
    def configure_app(self, user_id : str, agent_id : str, config : dict[str, Any]):
        with self._lock:
            if user_id in self._user_apps and agent_id in self._user_apps[user_id]:
                agent : Agent = self._agents_apps[agent_id]
                if agent.is_running():
                    raise AgentException(f"{Agent.__name__} with id={agent_id} cannot be configured, while it's running.")
                else:
                    pass            

    def remove_app(self, user_id : str, agent_id : str):
        with self._lock:
            if user_id in self._user_apps and agent_id in self._user_apps[user_id]:
                agent : Agent = self._agents_apps[agent_id]
                if agent.is_running():
                    raise AgentException(f"{Agent.__name__} with id={agent_id} cannot be removed, when it's running.")
                else:
                    self._agents_apps.pop(agent_id)
                    self._user_apps[user_id].remove(agent_id)
    
    
    
