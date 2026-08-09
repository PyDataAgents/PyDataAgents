from __future__ import annotations
import os
import threading
from typing import TYPE_CHECKING, Any, Type
from dataclasses import dataclass, field
import uuid
from loguru import logger


from .AgentStates import AgentElementState, ServiceState
from ..utils.ClassUtils import ClassUtils
from .AgentElementException import AgentElementException
from .AgentException import AgentException
from ..nodes.Node import Node
from .AgentElement import AgentElement
from ..services.statemachine.StatemachineService import StatemachineService
from .AgentKeywords import AgentKeywords

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
    save_folder : str = field(default=AgentKeywords.SAVE_FOLDER, metadata={"description": "folder to save the AgentElements in local files, if None, a default folder is created in the current working directory"})
        
    buffer_store : dict[str, Buffer] = field(default_factory=dict, metadata={"description": "dictionary of Buffers in the Agent"})
    service_store : dict[str, Service] = field(default_factory=dict, metadata={"description": "dictionary of Services in the Agent"})

    def __post_init__(self):
        """ initialize `Agent` instance after dataclass initialization.        
        """
        self._is_running = False
        self._stop_event = threading.Event()
    
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
                logger.error(e)
                    
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
        return ClassUtils.config_options(self, with_descriptions)
        
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
                    logger.error(e)
    
    def release(self, blocking : bool = False):
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
            
        self._start_services()
        
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
                for _, service in self.service_store.items():                    
                    if service.contains_element(id):
                        services_for_restart.append(service)
                    if isinstance(service, StatemachineService):
                        for _, node in service.nodes.items():
                            if node.contains_element(id):
                                elements_for_reinstall.append(node)
                                services_for_restart.append(service)
            elif isinstance(agent_element, Service):
                services_for_restart.append(agent_element)                
            elif isinstance(agent_element, Node):
                for _, service in self.service_store.items():
                    if isinstance(service, StatemachineService):
                        if service.contains_element(id):
                            services_for_restart.append(service)
            elif isinstance(agent_element, AgentElement):
                for _, service in self.service_store.items():
                    if service.contains_element(id):
                        services_for_restart.append(service)
                    if isinstance(service, StatemachineService):
                        for _, node in service.nodes.items():
                            if node.contains_element(id):
                                elements_for_reinstall.append(node)
                                services_for_restart.append(service)
                for _, buffer in self.buffer_store.items():
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