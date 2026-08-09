from __future__ import annotations
from dataclasses import dataclass, field
import os
import secrets

from loguru import logger
from nicegui import ui


from ..app.AgentApp import AgentApp
from ..ui.UIAgentStorePages import UIAgentStoreLoginPage, UIAgentStorePage
from ..AgentStore import AgentStore


@dataclass
class AgentStoreApp(AgentApp):
    """ Application that stores an `AgentStore` and provides a REST API and UI based on configuration settings """
    
    with_ui : bool = field(default=True, metadata={"description": "Whether to create a UI for the agent store"})
     
    def __post_init__(self):
        self._agent_store : AgentStore = None
        
    def set_agent_store(self, agent_store : AgentStore):
        self._agent_store = agent_store
        
    def create(self, no_default_apis : bool = True, no_default_pages : bool = True):
        """ create the UI for the agent store """
        self.add_ui_page(UIAgentStoreLoginPage())
        self.add_ui_page(UIAgentStorePage())
        super().create(no_default_apis=no_default_apis, no_default_pages=no_default_pages)
    
    def run(self):
        """ Run the the agent store application. This will block the current thread until the application is stopped. """
        pages_paths = [f"http://{self.host}:{self.port}{page.path}" for page in self.ui_pages]
        pages_str = "\n".join(pages_paths)
        logger.info("Available NiceGui Pages:\n" + pages_str)                
        os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
        #app.add_middleware(AuthenticationMiddleware)
        ui.run(host=self.host, port = self.port, reload=True, title=self.__class__.__name__ + " UI", storage_secret=secrets.token_hex(32))        
    
    def get_agent_store(self) -> AgentStore:
        return self._agent_store
        