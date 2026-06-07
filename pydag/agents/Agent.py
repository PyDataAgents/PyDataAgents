from __future__ import annotations
import multiprocessing
import os
from pathlib import Path
import threading
from typing import TYPE_CHECKING, Any, Type, cast
from dataclasses import dataclass, field
import uuid
from fastapi import APIRouter, Depends, FastAPI
from loguru import logger
from nicegui import app, ui
import uvicorn

from pydag.agents.AgentStates import AgentElementState, ServiceState
from fastapi.middleware.cors import CORSMiddleware
from pydag.agents.api.AgentRESTAPI import AgentRESTAPI
from pydag.agents.api.BufferRESTAPI import BufferRESTAPI
from pydag.agents.api.NodeRESTAPI import NodeRESTAPI
from pydag.agents.api.RESTAPIManager import APIRole, RESTAPIManager
from pydag.agents.api.ServiceRESTAPI import ServiceRESTAPI
from pydag.agents.ui.UIAgentMgmtPage import UIAgentMgmtPage
from pydag.agents.ui.UIBufferPage import UIBufferPage
from pydag.agents.ui.UIElements import UIHomePage, UIPage
from pydag.utils.ClassUtils import ClassUtils

from .AgentElementException import AgentElementException
from .AgentException import AgentException
from ..utils.FileUtils import FileUtils
from .YAMLConfig import YAMLConfig
from ..nodes.Node import Node
from .AgentElement import AgentElement
from .AgentConfig import AgentConfig
from ..services.statemachine.StatemachineService import StatemachineService
from ..services.MappingService import MappingService
from ..services.ObserverService import ObserverService
from ..nodes.BufferNode import BufferNode

if TYPE_CHECKING:
    from ..buffers.Buffer import Buffer
    from ..services.Service import Service


@dataclass
class Agent():
    """ `Agent` class for managing a multi-component application system.
    The `Agent` serves as the central orchestrator for managing Buffers, Nodes and Services.
    It handles the lifecycle of these components including installation, initialization, connection,
    and termination. The `Agent` supports optional features such as persistence, REST API exposure,
    and configurable startup behavior.
    
    Args:
        id (str): Unique identifier for the `Agent` application. Auto-generated if not provided.
        create_config (bool): If True, creates a configuration YAML file on startup. Defaults to False.
        load_on_install (bool): If True, all `AgentElements` are set to load_on_install=True. Defaults to False.
        with_persistence (bool): If True, an `AgentPersistService` is created by default to continuously
            save `AgentElements` to local files. Defaults to False.
        with_rest_api (bool): If True, a REST API `Service` is created by default for REST interactions
            on port 4700. Defaults to False.
        description (str): Application/agent description. Defaults to None.
        buffer_store (dict[str, Buffer]): Dictionary storing all `Buffer` instances in the `Agent`.
        service_store (dict[str, Service]): Dictionary storing all `Service` instances in the `Agent`.
            to install or uninstall.
    Raises:
        AgentException: _description_
        AgentException: _description_

    Returns:
        _type_: _description_
    """
    
    id : str = field(default_factory=lambda: str(uuid.uuid4()), metadata = {"description": "unique identifier of Agent"})
    description : str = field(default=None, metadata={"description": "application/agent description"})    
    create_config : bool = field(default=False, metadata={"description": "creates a configuration yaml on start, when True"})
    load_on_install : bool = field(default=False, metadata={"description": "if True, all AgentElements are set to load_on_install = True"})
    with_persistence : bool = field(default=False, metadata={"description": "if True, an AgentPersistService is created by default to contuinously save the AgentElements in a local files"})
    
    port : int = field(default=8081, metadata={"description": "port for the REST API Service"})
    with_api : bool = field(default=False, metadata={"description": "if True, a REST API Service is created by default for REST interactions on port specified in port"})
    api_key_file : str = field(default=None, metadata={"description": "file path for API key storage and loading"})
    with_ui : bool = field(default=False, metadata={"description": "if True, a NiceGUI UI is created by default for the Agent"})
    dark_mode : bool = field(default=True, metadata={"description": "enables dark mode"})
    color_schema : dict = field(default_factory=dict, metadata={"description": "color schema for the ui, see https://nicegui.io/docs/colors for more details"})
    
    buffer_store : dict[str, Buffer] = field(default_factory=dict, metadata={"description": "dictionary of Buffers in the Agent"})
    service_store : dict[str, Service] = field(default_factory=dict, metadata={"description": "dictionary of Services in the Agent"})

    def __post_init__(self):
        """ initialize `Agent` instance after dataclass initialization.        
        """
        self._is_running = False
        self._stop_event = threading.Event()
        self._app : FastAPI = None
        self._ui_pages : list[UIPage] = []
    
    def _install_elements(self):
        """ install all `Node`s, `Buffer`s, and `Service`s in the `Agent`.
        
        iterates over each element and calls its install method with the `Agent` instance. 
        
        Raises:
            AgentElementException: if a `AgentElement` could not be installed
        """
        # check all with_xxx options to create services by default
        if self.with_persistence:
            from ..services.utils.AgentPersistService import AgentPersistService
            from ..services.ThreadType import ThreadType
            aps = AgentPersistService(thread_type=ThreadType.SECOND.value, observing_time=3600)
            self.add_service(aps)
            
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during installs
        for buffer in list(self.buffer_store.values()):
            try:
                buffer.install(self) # nodes are installed via its service
                if self.load_on_install:
                    buffer.load_on_install = True
            except AgentElementException as e:
                logger.error(f"Could not install{buffer.__class__.__name__} with {buffer.config_options()}: {e}")
        for service in list(self.service_store.values()):
            try:
                service.install(self) # nodes are installed via its service
                if self.load_on_install:
                    service.load_on_install = True
            except AgentElementException as e:
                logger.error(f"Could not install{service.__class__.__name__} with {service.config_options()}: {e}")
                    
    def _uninstall_elements(self):
        """ uninstall all `Node`s, `Buffer`s, and `Service`s from the `Agent`.
        
        iterates over each element and calls its uninstall method.
        """
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during uninstalls
        for buffer in list(self.buffer_store.values()):
            buffer.uninstall(self)
        for service in list(self.service_store.values()):
            service.uninstall(self)
    
    def add_buffer(self, buffer : Buffer):
        """Add a `Buffer` to the `Agent`'s buffer store.
        
        Args:
            buffer (Buffer): the Buffer instance to add.
        """
        if buffer.id in self.buffer_store:
            logger.warning(f"A {buffer.__class__.__name__} with id='{buffer.id}' already exists in {self.__class__.__name__}'s buffer_store and is overwritten!")        
        self.buffer_store[buffer.id] = buffer
        # in order to make duplicate buffers and their ids available in agent for later elements or acces (in scripts), we install them right away
        if len(buffer.duplicate_ids) > 0:
            buffer.install(self)
        
    def add_service(self, service : Service):
        """Add a Service to the Agent's service store.
        
        Args:
            service (Service): The Service instance to add.
        """
        if service.id in self.service_store:
            logger.warning(f"A {service.__class__.__name__} with id='{service.id}' already exists in {self.__class__.__name__}'s service_store and is overwritten!")
        self.service_store[service.id] = service
           
    def config_options(self, with_descriptions = False) -> dict:
        """ get the configuration options for the whole `Agent`.
        
        Args:
            with_descriptions (bool, optional): Whether to include descriptions. Defaults to False.
        
        Returns:
            dict: Configuration options dictionary.
        """
        return AgentConfig.config_options(self, with_descriptions)
        
    def _stop_services(self):
        """ Stop all `Service`s in the `Agent`.
        """
        for service in self.service_store.values():
            service.stop()          
                
    def _start_services(self):
        """ Start all `Service`s in the `Agent`
        
        Raises:
            ServiceException: if a `Service` could not be startedf
        """
        for service in self.service_store.values():
            if service.auto_start:
                try:
                    service.start()
                except AgentElementException as e:
                    logger.error(f"Could not start {service.__class__.__name__}: {e}")
    
    @staticmethod
    def load_from(config_file : str) -> Agent:
        """ loads an `Agent` from configuration file `config_file`

        Args:
            config_file (str): path to a config file, only YAML is implemented so far

        Raises:
            AgentException: if the `Agent` cannot be configured from `config_file`

        Returns:
            Agent: an `Agent` instance
        """
        if FileUtils.exists_file(config_file):
            ext = Path(config_file).suffix
            match(ext):
                case ".yaml" | ".yml":
                    yc = YAMLConfig(config_file)
                    ac : AgentConfig = yc.load()
                    ag : Agent = AgentConfig.create(ac)
                    return ag
                case _:
                    raise AgentException(f"Unknown File Type for {Agent.__name__} configuration (only YAML is supported)")
        else:
            raise AgentException(f"Configuration File {config_file} was not found!")
    
    def release(self, blocking : bool = True):
        """Release the `Agent` for operation.
        
        Installs all elements and starts services. If blocking is True,
        waits until the stop event is set (typically by calling terminate()).
        
        Args:
            blocking (bool, optional): Whether to block until Agent is terminated. Defaults to True.
            
        Raises:
            ServiceException: if a `Service` could not be started
            AgentElementException: if a `AgentElement` could not be installed
        """
        self._install_elements()
        if self.create_config:
            gc = AgentConfig(self)
            yc = YAMLConfig(f"Agent {self.id}.yaml")
            yc.save(gc)
        self._start_services()
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
        else:
            self._stop_event.clear()
            self._is_running = True
            logger.info(f"Started {self.__class__.__name__} application (id='{self.id}')")
            if blocking:
                self._stop_event.wait()  # blocks efficiently until the event is set (for example by terminate)
                
    def terminate(self):
        """ Terminate the `Agent`.
        
        Stops all services and uninstalls elements.
        Signals the stop event to unblock any waiting release() call.
        """
        self._stop_services()
        self._uninstall_elements()
        self._is_running = False
        self._stop_event.set()
        
    def get_buffer(self, id : str) -> Buffer:
        """ return the `Buffer` specified by `id`, if the specified `Buffer` is not found, the method returns `None

        Args:
            id (str): unique id of the `Buffer`

        Returns:
            Buffer: `Buffer` instance
        """
        if id in self.buffer_store:
            return self.buffer_store[id]    
        else:
            logger.error(f"No Buffer with id={id} was found")
            return None
        
    def get_service(self, id : str) -> Service:
        """ return the `Service` specified by `id`
        """
        if id in self.service_store:
            return self.service_store[id]    
        else:
            logger.error("No Service with id=" + id + " was found")
            return None
        
    def get_services(self, type : Type) -> list[Service]:
        """returns all services of a specified type/class

        Args:
            type (Type): class

        Returns:
            list[Service]: list of services with the specified type
        """
        services = list()
        for service in self.service_store.values():
            if isinstance(service, type):
                services.append(service)
        return services
           
    def get_element(self, id : str) -> AgentElement:
        """Return the `AgentElement` with the specified `id`.
        """        
        if id in self.buffer_store:
            return self.buffer_store[id]
        elif id in self.service_store:
            return self.service_store[id]
        else:
            return self._get_deep_element(id)
            
    def get_node(self, id : str, service_id : str = None) -> Node:
        """Return the `Node` with the specified `id`.

        If `service_id` is given, the search is limited to that `Service` (expected to be a
        `StatemachineService`). Otherwise, all services are searched for a node with the
        matching id.

        Args:
            id (str): Unique id of the `Node` to retrieve.
            service_id (str, optional): Unique id of the `Service` to restrict the search to.
                Defaults to None.

        Returns:
            Node: The `Node` instance if found, otherwise `None`.
        """
        if service_id:
            service = self.get_service(service_id)
            if service:
                if isinstance(service, StatemachineService):
                    if id in service.nodes:
                        return service.nodes[id]
                    else:
                        logger.error(f"specified {Node.cname()} with id={id} was not found in  with id={service_id}")                        
                else:
                    logger.error(f"specified Service is not of type {StatemachineService.cname()}")     
                    return None
            else:
                logger.error(f"no Service with id={service_id} was found!")
                return None
        else:
            node : Node = None
            for service in self.service_store.values():            
                if isinstance(service, StatemachineService):
                    if id in service.nodes:
                        node =  service.nodes[id]
            if node:
                return node
            else:
                logger.error(f"no {Node.cname()} with id={id} was found!")
                return None
    
    def edit_element(self, id : str, config_options : dict[str, Any]):
        """ edits the `AgentElement` specified by id with the given `config_options` 
        and correctly stops / reinstalls / starts associated `AgentElement`'s
        
        Args:
            id: 
            config_options:
            
        """
        agent_element : AgentElement = self.get_element(id)
        if agent_element:
            from ..buffers.Buffer import Buffer
            from ..services.Service import Service
            services_for_restart : list[Service] = []
            elements_for_reinstall : list[AgentElement] = []
            elements_for_reinstall.append(agent_element)                
            if isinstance(agent_element, Buffer):
                for k, service in self.service_store.items():                    
                    if service.contains_element(id):
                        services_for_restart.append(service)
                    if isinstance(service, StatemachineService):
                        for kk, node in service.nodes.items():
                            if node.contains_element(id):
                                elements_for_reinstall.append(node)
                                services_for_restart.append(service)
            elif isinstance(agent_element, Service):
                services_for_restart.append(agent_element)                
            elif isinstance(agent_element, Node):
                for k, service in self.service_store.items():
                    if isinstance(service, StatemachineService):
                        if service.contains_element(id):
                            services_for_restart.append(service)
            elif isinstance(agent_element, AgentElement):
                for k, service in self.service_store.items():
                    if service.contains_element(id):
                        services_for_restart.append(service)
                    if isinstance(service, StatemachineService):
                        for kk, node in service.nodes.items():
                            if node.contains_element(id):
                                elements_for_reinstall.append(node)
                                services_for_restart.append(service)
                for k, buffer in self.buffer_store.items():
                    if buffer.contains_element(id):
                        elements_for_reinstall.append(buffer)
            
            # stop all required services
            for service in services_for_restart:
                if service.get_state() == ServiceState.RUNNING:
                    service.stop()
                    
            # uninstall all required elements
            for element in  elements_for_reinstall:
                element.uninstall(self)
                
            # set new properties
            ClassUtils.set_properties(agent_element, config_options)
            
            # install all required elements
            for element in elements_for_reinstall:
                element.install(self)
                
            # restart required services
            for service in services_for_restart:
                if service.get_state() == AgentElementState.INSTALLED:
                    service.start()
        else:
            raise AgentException(f"Could not find any {AgentElement.__name__} with id={id} in {Agent.__name__}")                
    
    def _get_deep_element(self, id : str) -> AgentElement:
        """checks for nested `AgentElement`s

        Args:
            id (str): unique id

        Returns:
            AgentElement:
        """
        for service in self.service_store.values():
            for attr_name, attr_value in vars(service).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    return Agent._recursive_element_search(attr_value, id)

            # special case for statemachine services, look into nodes
            if isinstance(service, StatemachineService):
                for node in service.nodes.values():
                    return Agent._recursive_element_search(node, id)
        
        for buffer in self.buffer_store.values():
            for attr_name, attr_value in vars(buffer).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    return Agent._recursive_element_search(attr_value, id)
        return None
    
    @staticmethod
    def _recursive_element_search(root_element : AgentElement, id : str) -> AgentElement:
        if root_element.id == id:
            return root_element
        else:
            for attr_name, attr_value in vars(root_element).items():
                if isinstance(attr_value, AgentElement):
                    if attr_value.id == id:
                        return attr_value
                    return Agent._recursive_element_search(attr_value, id)
        
    def is_running(self) -> bool:
        """Check if the Agent is currently running.
        
        Returns:
            bool: True if the Agent is running, False otherwise.
        """
        return self._is_running
        
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
       