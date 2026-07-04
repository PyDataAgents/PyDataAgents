from __future__ import annotations
from dataclasses import dataclass, field
import os
import secrets
from threading import Lock
from typing import Any
import uuid

from loguru import logger
from nicegui import app, ui


from .auth.Auth import AuthenticationMiddleware
from .ui.UIAgentStorePages import UIAgentStoreLoginPage, UIAgentStorePage
from .ui.UIElements import UIPage
from .AgentException import AgentException
from .YAMLConfig import YAMLConfig
from .AgentConfig import AgentConfig
from ..utils.FileUtils import FileUtils
from .Agent import Agent

@dataclass
class AgentStore:
    """A store for managing template based agents, that users can create in a multi-client setup."""
    
    template_paths : list[str] = field(default_factory=list, metadata={"description": "List of paths to agent templates"})
    host : str = field(default="localhost", metadata={"description": "Host for the agent store server"})
    port : int = field(default=10001, metadata={"description": "Port for the agent store server"})
    
    def __post_init__(self):
        self._user_agents : dict[str, list[str]] = dict()
        self._agents : dict[str, Agent] = dict()
        self._templates : dict[str, AgentConfig] = dict()
        self._lock : Lock = Lock()
        self._ui_pages : list[UIPage] = list()
    
    def open(self):
        """ Start the agent store UI Server. This will block the current thread until the server is stopped. """        
        self.load_templates()
        self.create_ui()
        pages_paths = [f"http://{self.host}:{self.port}{page.path}" for page in self._ui_pages]
        pages_str = "\n".join(pages_paths)
        logger.info("Available NiceGui Pages:\n" + pages_str)                
        os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
        #app.add_middleware(AuthenticationMiddleware)
        ui.run(host=self.host, port = self.port, reload=True, title=self.__class__.__name__ + " UI", storage_secret=secrets.token_hex(32))        
    
    def close(self):
        """ Close the agent store UI Server. """
        app.shutdown() 
                
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
                self._user_agents[user_id] = []
    
    def add_agent(self, user_id : str, agent : Agent):
        with self._lock:
            if user_id in self._user_agents:
                self._user_agents[user_id].append(agent.id)
            self._agents[agent.id] = agent
            
    def add_agent_from_template(self, user_id : str, template_id : str):
        with self._lock:
            if template_id in self._templates:
                agent_config = self._templates[template_id]
                new_agent = agent_config.create()
                new_agent.id = str(uuid.uuid4())
                self._agents[new_agent.id] = new_agent
            else:
                raise AgentException(f"Template with ID {template_id} not found.")
            
    def get_agent(self, user_id : str, agent_id : str) -> Agent:
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                return self._agents[agent_id]
            else:
                return None
        
    def get_templates(self) -> dict[str, AgentConfig]:
        with self._lock:
            return self._templates
            
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
                
    def configure_agent(self, user_id : str, agent_id : str, config : dict[str, Any]):
        with self._lock:
            if user_id in self._user_agents and agent_id in self._user_agents[user_id]:
                # TODO : Implement agent configuration logic here
                pass

    def create_ui(self):
        """ create the UI for the agent store """
        p = UIAgentStoreLoginPage(None)
        self._ui_pages.append(p)
        p = UIAgentStorePage(self)
        self._ui_pages.append(p)
        for page in self._ui_pages:
            page.register()
        
    
