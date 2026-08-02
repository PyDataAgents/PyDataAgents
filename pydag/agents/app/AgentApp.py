from __future__ import annotations
from dataclasses import dataclass, field
import multiprocessing
import os
from pathlib import Path
import uvicorn
import yaml
from loguru import logger
from nicegui import app, ui
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


from ...utils.ClassUtils import ClassUtils
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

    host : str = field(default="localhost", metadata={"description": ""})
    port : int = field(default=8081, metadata={"description": "port for the REST API Service"})
    with_api : bool = field(default=False, metadata={"description": "if True, a REST API Service is created by default for REST interactions on port specified in port"})
    api_key_file : str = field(default=None, metadata={"description": "file path for API key storage and loading"})
    with_ui : bool = field(default=False, metadata={"description": "if True, a NiceGUI UI is created by default for the Agent"})
    dark_mode : bool = field(default=True, metadata={"description": "enables dark mode"})
    color_schema : dict = field(default_factory=dict, metadata={"description": "color schema for the ui, see https://nicegui.io/docs/colors for more details"})
    with_config : bool = field(default=False)
    agent : Agent = field(default_factory=Agent, metadata={"description": "the `Agent` instance to be used by the `AgentApp`"})
    ui_pages : list[UIPage] = field(default_factory=list, metadata={"description": "list of UIPage instances to be used by the `AgentApp`"})
    
    def __post_init__(self):
        self._app : FastAPI = None
        
    @staticmethod
    def load(config : str | dict) -> AgentApp:
        """ loads the `AgentApp` from file or dictionary """
        if isinstance(config, str):
            p : Path = Path(config)
            if p.exists():
                ext : str = config.split(".")[-1].lower()
                match ext:
                    case "yaml" | "yml":
                        with open(config, encoding="utf-8") as f:
                            app_config : dict = yaml.safe_load(f)
                            aa : AgentApp = AgentApp()
                            ClassUtils.set_properties(aa, app_config)
                            return aa
                    case _:
                        raise AgentException(f"loading from {config} is not defined")
            else:
                raise AgentException(f"{config} is not a valid filepath")
        elif isinstance(config, dict):            
            aa : AgentApp = AgentApp()
            ClassUtils.set_properties(aa, config)
            return aa
        else:
            raise AgentException("config was not of allowd datatypes (str | dict)")
    
    def create(self, no_default_apis : bool = False, no_default_pages : bool = False):
        """ Creates the `AgentApp` with the specified configuration.
                    
        Args:
            no_default_apis (bool, optional): If True, no default REST API endpoints will be created. Defaults to False.
            no_default_pages (bool, optional): If True, no default NiceGUI pages will be created. Defaults to False.        
        """
        if self.with_api:
            self._create_api(no_default_apis=no_default_apis)
        if self.with_ui:           
            self._create_ui(no_default_pages=no_default_pages)
        if self.with_config:
            self._create_config()
               
    def run(self):
        """ Runs the `AgentApp` with the specified configuration.
            This method is blocking.
        """
        if self.with_ui:
            os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", f"{self.port}")
            pages_paths = [f"http://{self.host}:{self.port}{page.path}" for page in self.ui_pages]
            pages_str = "\n".join(pages_paths)
            logger.info("Available NiceGui Pages:\n" + pages_str)
            self.agent.release(blocking=False)        
            if self.with_api:
                multiprocessing.freeze_support()  # For Windows support
                ui.run_with(self._app, dark=self.dark_mode, title=self.__class__.__name__ + " UI")
                uvicorn.run(self._app, host=self.host, port=self.port, reload=False, workers=1)            
            else:
                ui.run(host=self.host, port = self.port, reload=False, dark=self.dark_mode, title=self.__class__.__name__ + " UI")
        else:                
            if self.with_api:
                logger.info("Available FastAPI url:\n" + self._app.docs_url)
                self.agent.release(blocking=False)
                multiprocessing.freeze_support()  # For Windows support
                uvicorn.run(self._app, host=self.host, port=self.port, reload=False, workers=1)
            else:
                self.agent.release(blocking=True)
    
    def shutdown(self):
        """ Shuts down the `AgentApp` and the `Agent` instance. """
        self.agent.terminate()
        if self.with_ui:
            if self.with_api:
                pass            
            else:
                pass
        else:                
            if self.with_api:
                pass
                            
    def _create_api(self, no_default_apis : bool = False):
        """ Create a FastAPI REST API for the Agent.
        This method initializes the FastAPI app and sets up the REST API endpoints.
        Args:
            no_default_apis (bool, optional): If True, no default REST API endpoints will be created. Defaults to False.
        """
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
         
    def _create_ui(self, no_default_pages : bool = False):
        """Create a NiceGUI UI for the Agent.
        This method initializes the NiceGUI app and sets up the UI pages.
        """
        if not no_default_pages:
            self.add_ui_page(UIHomePage())
            self.add_ui_page(UIBufferPage(1.0 / 30.0))
            self.add_ui_page(UIAgentMgmtPage(1.0))
        
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
        for page in self.ui_pages:
            page.register(self)
    
    def config_options(self) -> dict:
        """ Returns a dictionary of configuration options for the `AgentApp` instance.
        
        Returns:
            dict: A dictionary containing the configuration options and their values.
        """
        return ClassUtils.config_options(self)
    
    def _create_config(self):
        apc = self.config_options()
        yaml_file = open(f"{self.get_agent().id}.yaml", "w", encoding='utf-8')
        yaml.dump(apc, yaml_file, sort_keys=False)
        yaml_file.close()
    
    def add_api(self, router : APIRouter):
        """ Add a REST API router to the FastAPI app.
        
        Args:
            router (APIRouter): The FastAPI router to be added.
        """
        self._app.include_router(router)
            
    def add_ui_page(self, page : UIPage):
        """ Add a NiceGUI UI page to the AgentApp. 
        
        Args:
            page (UIPage): The NiceGUI UI page to be added.        
        """
        self.ui_pages.append(page)
        
    def remove_ui_page(self, i : int):
        """ Remove a NiceGUI UI page from the AgentApp by index.
        
        Args:
            i (int): The index of the page to be removed.
        """
        self.ui_pages.pop(i)
        
    def clear_ui_pages(self):
        """ Clear all NiceGUI UI pages from the AgentApp. """
        self.ui_pages.clear()

    def get_ui_pages(self) -> list[UIPage]:
        """ Get the list of NiceGUI UI pages in the AgentApp.
        
        Returns:
            list[UIPage]: The list of NiceGUI UI pages.
        """
        return self.ui_pages
    
    def set_agent(self, ag : Agent):
        """ Set the `Agent` instance for the `AgentApp`.
        
        Args:
            ag (Agent): The `Agent` instance to be set.
        """
        self.agent = ag
        
    def get_agent(self) -> Agent:
        """ Get the `Agent` instance associated with the `AgentApp`.
        
        Returns:
            Agent: The `Agent` instance associated with the `AgentApp`.
        """
        return self.agent
        
    def set_app(self, fast_api_app : FastAPI):
        """ Set the FastAPI app for the `AgentApp`.
        
        Args:
            fast_api_app (FastAPI): The FastAPI app to be set.
        """
        self._app = fast_api_app