from __future__ import annotations
from dataclasses import dataclass, field
import multiprocessing
from threading import Lock
from typing import Any
import uuid
from loguru import logger

from .app.AgentApp import AgentApp
from .app.AppException import AppException
from .AgentKeywords import AgentKeywords
from ..utils.FileUtils import FileUtils

def _run_app_process(app_config: dict) -> None:
    aa : AgentApp = AgentApp.load(app_config)
    aa.create()
    aa.run()

@dataclass
class AgentStore:
    """A store for managing template based agents, that users can create in a multi-client setup."""
    
    template_paths : list[str] = field(default_factory=list, metadata={"description": "List of paths to agent templates"})
    
    def __post_init__(self):
        self._users : dict[str, set[str]] = dict() # user_id -> set of unique config_id's for each app config created for that user
        self._configs : dict[str, dict] = dict() # config_id -> corresponding app config for that id
        self._templates : dict[str, dict] = dict() # template_id -> dict of corresponding app config for that template
        self._processes: dict[str, multiprocessing.Process] = {} # config_id -> process for that app
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
                raise AppException(f"Template config does not contain an 'id' field. Cannot add template.")
    
    def _add_user_unlocked(self, user_id : str):
        if user_id not in self._users:
            self._users[user_id] = set()
    
    def add_user(self, user_id : str):
        with self._lock:
            self._add_user_unlocked(user_id)
    
    def _add_user_config_unlocked(self, user_id : str, config_id : str, config : dict):
        if not user_id in self._users:
            self._add_user_unlocked(user_id)
            self._users[user_id].add(config_id)
            self._configs[config_id] = config
    
    def add_user_config(self, user_id : str, config_id : str, config : dict):
        with self._lock:            
            self._add_user_config_unlocked(user_id, config_id, config)
            
    def add_app_from_template(self, user_id : str, template_id : str):
        with self._lock:
            if template_id in self._templates:
                app_config = self._templates[template_id]
                config_id = str(uuid.uuid4())
                app_config[AgentKeywords.AGENT][AgentKeywords.ID] = config_id
                self._add_user_config_unlocked(user_id, config_id, app_config)
            else:
                raise AppException(f"Template with ID {template_id} not found.")
    
    def get_templates(self) -> dict[str, dict]:
        with self._lock:
            return self._templates
            
    def get_users(self) -> list[str]:
        with self._lock:
            return list(self._users.keys())
        
    def get_user_configs(self, user_id : str) -> list[dict]:
        with self._lock:
            if user_id in self._users:
                return [self._configs[config_id] for config_id in self._users[user_id] if config_id in self._configs]
            else:
                return []
    
    def _run_app_unlocked(self, config_id) -> multiprocessing.Process:
        if config_id not in self._configs:
            raise AppException(f"No app config with id={config_id} was found in the store.")
        existing_process = self._processes.get(config_id)
        if existing_process is not None and existing_process.is_alive():
            return existing_process
        app_config = self._configs[config_id]
        context = multiprocessing.get_context("spawn")
        process = context.Process(target=_run_app_process, args=(app_config,), daemon=True)
        process.start()
        self._processes[config_id] = process
        return process
    
    def run_app(self, config_id: str) -> multiprocessing.Process:
        with self._lock:
            return self._run_app_unlocked(config_id)
    
    def _shutdown_app_unlocked(self, config_id : str):
        process = self._processes.get(config_id)
        if process is None:
            return
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
        self._processes.pop(config_id, None)
    
    def shutdown_app(self, config_id: str):
        with self._lock:
            self._shutdown_app_unlocked(config_id)
                
    def configure_app(self, user_id : str, config_id : str, config : dict[str, Any]):
        with self._lock:
            if user_id in self._users and config_id in self._configs:
                if config_id in self._processes:
                    process = self._processes[config_id]
                    if process.is_alive():
                        logger.warning("The app is already running config found for user_id='{user_id}' and config_id='{config_id}', the app will be shutdown and run anew.")                    
                    self._add_user_config_unlocked(user_id, config_id, config)
                    self._shutdown_app_unlocked(config_id)
                    self._run_app_unlocked(config_id)
                else:
                    raise AppException(f"No process was found for config_id='{config_id}'")
            else:
                raise AppException(f"No app config found for user_id='{user_id}' and config_id='{config_id}'")            

    def remove_app(self, user_id : str, config_id : str):
        with self._lock:
            if user_id in self._users and config_id in self._configs and config_id in self._processes:
                self._configs.pop(config_id)
                self._shutdown_app_unlocked(config_id)
            else:
                logger.warning("No app config found for user_id='{user_id}' and config_id='{config_id}'")