from dataclasses import dataclass, field
import os
import secrets

from fastapi import FastAPI
from loguru import logger
from nicegui import app, ui


from ..ui.UIAgentStorePages import UIAgentStoreLoginPage, UIAgentStorePage
from ..ui.UIElements import UIPage
from ..AgentStore import AgentStore


@dataclass
class AgentStoreApp:
    """ Application that stores an `AgentStore` and provides a REST API and UI based on configuration settings """
    
    host : str = field(default="localhost", metadata={"description": "Host for the agent store server"})
    port : int = field(default=10001, metadata={"description": "Port for the agent store server"})
    
    
    def __init__(self):
        self._agent_store : AgentStore = None
        self._app : FastAPI = None
        self._ui_pages : list[UIPage] = list()
        
    def create(self):
        """ create the UI for the agent store """
        # define default color schema
        
        app.colors(
            primary='#005B95',
            secondary='#A8A8A9',
            accent='#C43726',
            positive='#00B050', 
            negative='#C43726',
        )
        
        p = UIAgentStoreLoginPage(None)
        self._ui_pages.append(p)
        p = UIAgentStorePage(self)
        self._ui_pages.append(p)
        for page in self._ui_pages:
            page.register()            
    
    def run(self):
        self.create()
        pages_paths = [f"http://{self.host}:{self.port}{page.path}" for page in self._ui_pages]
        pages_str = "\n".join(pages_paths)
        logger.info("Available NiceGui Pages:\n" + pages_str)                
        os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
        #app.add_middleware(AuthenticationMiddleware)
        ui.run(host=self.host, port = self.port, reload=True, title=self.__class__.__name__ + " UI", storage_secret=secrets.token_hex(32))        
    
        