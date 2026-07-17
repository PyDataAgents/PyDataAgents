from __future__ import annotations
from dataclasses import dataclass, field
import multiprocessing
import os
import uvicorn
import yaml
from loguru import logger
from nicegui import app, ui
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


from ..AgentConfig import AgentConfig
from ..api.AgentRESTAPI import AgentRESTAPI
from ..api.BufferRESTAPI import BufferRESTAPI
from ..api.NodeRESTAPI import NodeRESTAPI
from ..api.RESTAPIManager import APIRole, RESTAPIManager
from ..api.ServiceRESTAPI import ServiceRESTAPI
from ..ui.UIAgentMgmtPage import UIAgentMgmtPage
from ..ui.UIBufferPage import UIBufferPage
from ..ui.UIElements import UIHomePage, UIPage
from ..AgentException import AgentException
from ..Agent import Agent


@dataclass
class AgentApp():
    """ Application that stores an `Agent` and provides REST API and UI based on configuration settings """
        
    port : int = field(default=8081, metadata={"description": "port for the REST API Service"})
    with_api : bool = field(default=False, metadata={"description": "if True, a REST API Service is created by default for REST interactions on port specified in port"})
    api_key_file : str = field(default=None, metadata={"description": "file path for API key storage and loading"})
    with_ui : bool = field(default=False, metadata={"description": "if True, a NiceGUI UI is created by default for the Agent"})
    dark_mode : bool = field(default=True, metadata={"description": "enables dark mode"})
    color_schema : dict = field(default_factory=dict, metadata={"description": "color schema for the ui, see https://nicegui.io/docs/colors for more details"})
            
    def __post_init__(self):
        self._agent : Agent = field(default=None)    
        self._app : FastAPI = None
        self._ui_pages : list[UIPage] = []
    
    def set_agent(self, ag : Agent):
        self._agent = ag
        
    @staticmethod
    def load(file_path : str) -> AgentApp:
        ext : str = file_path.split(".")[-1].lower()
        match ext:
            case "yaml" | "yml":
                with open(file_path, encoding="utf-8") as f:
                    data : dict = yaml.safe_load(f)
                # split the config into app and agent config
                apcd : dict = data.copy()
                del apcd["agent"]
                acd : dict = data["agent"]
                ac : AgentConfig = AgentConfig.from_dict(acd)
                aa : AgentApp = AgentApp(**apcd)
                aa.set_agent(ac.create())
                return aa
            case _:
                raise AgentException(f"loading from {file_path} is not defined")
        
    def run(self):
        pass
    
    def _create_app(self):
    # create web api and ui if specified
        if self.with_api:
            self.create_api()
        if self.with_ui:
            self.create_ui()
        # check how to run the application, with blocking or non-blocking release or the blocking web api server (uvicorn/fastapi/nicegui)
        host="0.0.0.0"
        if self._app:
            if len(self._ui_pages) > 0:
                pages_paths = [f"http://{host}:{self.port}{page.path}" for page in self._ui_pages]
                pages_str = "\n".join(pages_paths)
                logger.info("Available NiceGui Pages:\n" + pages_str)
                os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
                ui.run_with(self._app, dark=self.dark_mode, title=self.__class__.__name__ + " UI")                
            multiprocessing.freeze_support()  # For Windows support
            uvicorn.run(self._app, host=host, port=self.port, reload=True, workers=1)
        elif len(self._ui_pages) > 0:
            pages_paths = [f"http://{host}:{self.port}{page.path}" for page in self._ui_pages]
            pages_str = "\n".join(pages_paths)
            logger.info("Available NiceGui Pages:\n" + pages_str)                
            os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
            ui.run(host=host, port = self.port, reload=True, dark=self.dark_mode, title=self.__class__.__name__ + " UI")
            
            
    def add_api(self, router : APIRouter):
        self._app.include_router(router)
    
    def create_api(self, no_default_apis : bool = False):
        if self.api_key_file:
            RESTAPIManager.generate_api_keys(api_key_file=self.api_key_file, agent=self) # Generate API keys and save to file if api_key_file is provided
            self._app = FastAPI(title=self.__class__.__name__ + " - REST API", docs_url="/docs", dependencies=[Depends(RESTAPIManager.require_min_role(APIRole.READ))])  # Protect all endpoints with API key dependency
        else:
            self._app = FastAPI(title=self.__class__.__name__ + " - REST API", docs_url="/docs")
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=False,
            allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
            allow_headers=["*"],  # Allows all headers
        )
        if not no_default_apis:
            self.add_api(AgentRESTAPI.get_api_router(self))
            self.add_api(BufferRESTAPI.get_api_router(self))
            self.add_api(ServiceRESTAPI.get_api_router(self))
            self.add_api(NodeRESTAPI.get_api_router(self))
         
    def create_ui(self, no_default_pages : bool = False):
        """Create a NiceGUI UI for the Agent.
        This method initializes the NiceGUI app and sets up the UI pages.
        """
        if not no_default_pages:
            self.add_ui_page(UIHomePage(self))
            self.add_ui_page(UIBufferPage(self, 1.0 / 30.0))
            self.add_ui_page(UIAgentMgmtPage(self, 1.0))
        
        # define default color schema        
        if len(self.color_schema) > 0:
            app.colors(**self.color_schema)
        else:
            app.colors(
                primary='#005B95',
                secondary='#A8A8A9',
                accent='#C43726',
                positive='#00B050', 
                negative='#C43726',
            )
            
        page : UIPage
        for page in self._ui_pages:
            page.register()
        
    def add_ui_page(self, page : UIPage):
        self._ui_pages.append(page)
        
    def remove_ui_page(self, i : int):
        self._ui_pages.pop(i)
        
    def clear_ui_pages(self):
        self._ui_pages.clear()

    def get_ui_pages(self) -> list[UIPage]:
        return self._ui_pages