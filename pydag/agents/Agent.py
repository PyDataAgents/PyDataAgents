from __future__ import annotations
from pathlib import Path
import threading
from typing import TYPE_CHECKING, Type, cast
from dataclasses import dataclass, field
import uuid
from loguru import logger



from .AgentException import AgentException
from ..utils.FileUtils import FileUtils
from .YAMLConfig import YAMLConfig
from ..nodes.Node import Node
from .AgentElement import AgentElement
from .AgentConfig import AgentConfig
from ..services.statemachine.StatemachineService import StatemachineService
from ..services.mappings.MappingService import MappingService
from ..services.ObserverService import ObserverService
from ..nodes.BufferNode import BufferNode

if TYPE_CHECKING:
    from ..adapters.Adapter import Adapter
    from ..buffers.Buffer import Buffer
    from ..services.Service import Service


@dataclass
class Agent():
    """ `Agent` class for managing a multi-component application system.
    The `Agent` serves as the central orchestrator for managing Adapters, Buffers, and Services.
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
        adapter_store (dict[str, Adapter]): Dictionary storing all `Adapter` instances in the `Agent`.
        service_store (dict[str, Service]): Dictionary storing all `Service` instances in the `Agent`.
            to install or uninstall.
    Raises:
        AgentException: _description_
        AgentException: _description_

    Returns:
        _type_: _description_
    """
    
    id : str = field(default=None, metadata={"description": "unique identifier of the Agent application"})
    create_config : bool = field(default=False, metadata={"description": "creates a configuration yaml on start, when True"})
    load_on_install : bool = field(default=False, metadata={"description": "if True, all AgentElements are set to load_on_install = True"})
    with_persistence : bool = field(default=False, metadata={"description": "if True, an AgentPersistService is created by default to contuinously save the AgentElements in a local files"})
    with_rest_api : bool = field(default=False, metadata={"description": "if True, a REST API Service is created by default to interact with the Agent via REST calls under port 4700"})
    description : str = field(default=None, metadata={"description": "application/agent description"})
    buffer_store : dict[str, Buffer] = field(default_factory=dict, metadata={"description": "dictionary of Buffers in the Agent"})
    adapter_store : dict[str, Adapter] = field(default_factory=dict, metadata={"description": "dictionary of Adapters in the Agent"})
    service_store : dict[str, Service] = field(default_factory=dict, metadata={"description": "dictionary of Services in the Agent"})

    def __post_init__(self):
        """ initialize `Agent` instance after dataclass initialization.
        
        Sets up the internal storage dictionaries for `Buffer`s, `Adapter`s, and `Service`s.
        Generates a unique ID if not provided.
        """
        if self.id is None: 
            self.id = f"{self.__class__.__name__} [{uuid.uuid4()}]"
        self._is_running = False
        self._stop_event = threading.Event()
    
    def _install_elements(self):
        """ install all `Adapter`s, `Buffer`s, and `Service`s in the `Agent`.
        
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
        if self.with_rest_api:
            from ..services.rest.RestService import RestService
            rs = RestService(port=4700)
            self.add_service(rs)
            
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during installs
        for adapter in list(self.adapter_store.values()):
            adapter.install(self)
            if self.load_on_install:
                adapter.load_on_install = True
        for buffer in list(self.buffer_store.values()):
            buffer.install(self)
            if self.load_on_install:
                buffer.load_on_install = True
        for service in list(self.service_store.values()):
            service.install(self)
            if self.load_on_install:
                service.load_on_install = True
        
    def _uninstall_elements(self):
        """ uninstall all `Adapter`s, `Buffer`s, and `Service`s from the `Agent`.
        
        iterates over each element and calls its uninstall method.
        """
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during uninstalls
        for adapter in list(self.adapter_store.values()):
            adapter.uninstall(self)
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
        
    def add_adapter(self, adapter : Adapter):
        """Add an Adapter to the Agent's adapter store.
        
        Args:
            adapter (Adapter): The Adapter instance to add.
        """
        if adapter.id in self.adapter_store:
            logger.warning(f"A {adapter.__class__.__name__} with id='{adapter.id}' already exists in {self.__class__.__name__}'s adapter_store and is overwritten!")
        self.adapter_store[adapter.id] = adapter
        
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
           
    def _disconnect_adapters(self):
        """ Disconnect all `Adapter`s in the `Agent`.
        
        Logs errors for adapters that fail to disconnect.
        """
        for adapter in self.adapter_store.values():
            if adapter.disconnect() is False:
                logger.error(adapter.name() + " could not be disconnected")
        
    def _stop_services(self):
        """ Stop all `Service`s in the `Agent`.
        """
        for service in self.service_store.values():
            service.stop()
                   
    def _connect_adapters(self):
        """ Connect all `Adapter`s in the `Agent`.        
        """
        for adapter in self.adapter_store.values():
            if adapter.connect() is False:
                logger.error(adapter.name() + " could not be connected")           
                
    def _start_services(self):
        """ Start all `Service`s in the `Agent`
        
        Raises:
            ServiceException: if a `Service` could not be startedf
        """
        for service in self.service_store.values():
            if service.auto_start:
                service.start()
    
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
        
        Installs all elements, connects adapters, and starts services. If blocking is True,
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
        #self._connect_adapters() # not included anymore, because mappings or nodes connect adapters on demand
        self._start_services()
        self._stop_event.clear()
        self._is_running = True
        logger.info(f"Started {self.__class__.__name__} application (id='{self.id}')")
        if blocking:
            self._stop_event.wait()  # blocks efficiently until the event is set (for example by terminate)
                
    def terminate(self):
        """ Terminate the `Agent`.
        
        Stops all services, disconnects adapters, and uninstalls elements.
        Signals the stop event to unblock any waiting release() call.
        """
        self._stop_services()
        #self._disconnect_adapters() # mappings and nodes disconnect adapters on demand
        self._uninstall_elements()
        self._is_running = False
        self._stop_event.set()
            
    def get_adapter(self, id : str) -> Adapter:
        """ return the `Adapter` specified by `id`
        Args:
            id (str): _description_

        Returns:
            Adapter: _description_
        """
        if id in self.adapter_store:
            return self.adapter_store[id]    
        else:
            logger.error("No Adapter with id=" + id + " was found")
            return None
        
    def get_buffer(self, id : str) -> Buffer:
        """ return the `Buffer` specified by `id`

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
        if id in self.adapter_store:
            return self.adapter_store[id]
        elif id in self.buffer_store:
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
    
    def state_tree(self) -> dict:
        """ returns a dictionary tree structure with (Mapping)Services and their contained Nodes, Adapters, Buffers
        and ObserverThreads with their respective state, possible next iterations or other relevant info

        Returns:
            dict: dictionary with element tree
        """
        tree : dict = {}
        service : Service
        for k, service in self.service_store.items():
            if isinstance(service, MappingService):
                sd : dict = {
                    "type": service.type,
                    "state": service.get_state(),
                    "last_update": service.get_observer_thread().get_last_update(),
                    "next_update": service.get_observer_thread().get_next_update(),
                    "adapter": {},
                    "buffers": {}
                }
                if service.get_adapter():
                    sd["adapter"] = {
                        "id": service.get_adapter().id,
                        "type": service.get_adapter().type,
                        "state": service.get_adapter().get_state()
                    }
                if len(service.get_buffers()) > 0:
                    buffer : Buffer
                    for kk, buffer in service.get_buffers().items():
                        bd = {
                            "type": buffer.type,
                            "size": buffer.size(),
                            "capacity": buffer.capacity,
                            "state": buffer.get_state(),
                            "last_access": buffer.get_last_access() 
                        }
                        sd["buffers"][buffer.id] = bd
                tree[service.id] = sd
            elif isinstance(service, StatemachineService):
                nds : dict = {}
                node : Node
                for kk, node in service.nodes.items():
                    nd : dict = {
                        "type": node.type,
                        "state": node.get_state(),
                        "last_execution": node.get_last_timestamp(),
                        "active": node.is_active(),
                    }
                    if isinstance(node, BufferNode):
                        if node.get_buffer():
                            nd["buffer"] = {
                                "id": node.get_buffer().id,
                                "type": node.get_buffer().type,
                                "size": node.get_buffer().size(),
                                "capacity": node.get_buffer().capacity,
                                "state": node.get_buffer().get_state(),
                                "last_access": node.get_buffer().get_last_access()
                            }
                        
                    nds[node.id] = nd
                sd : dict = {
                    "type": service.type,
                    "state": service.get_state(),
                    "last_update": service.get_observer_thread().get_last_update(),
                    "next_update": service.get_observer_thread().get_next_update(),
                    "nodes": nds                
                }
                tree[service.id] = sd
            elif isinstance(service, ObserverService):                
                sd : dict = {
                    "type": service.type,
                    "state": service.get_state(),
                    "last_update": service.get_observer_thread().get_last_update(),
                    "next_update": service.get_observer_thread().get_next_update()
                }
                tree[service.id] = sd
            else:
                sd : dict = {
                    "type": service.type,
                    "state": service.get_state()
                }
                tree[service.id] = sd
        return tree
    
    def _get_deep_element(self, id : str) -> AgentElement:
        """checks for nested `AgentElement`s

        Args:
            id (str): unique id

        Returns:
            AgentElement:
        """
        for adapter in self.adapter_store.values():
            for attr_name, attr_value in vars(adapter).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    if attr_value.id == id:
                        return attr_value
            for buffer in self.buffer_store.values():
                for attr_name, attr_value in vars(buffer).items():
                    #print(f"{attr_name}: {type(attr_value)}")
                    if isinstance(attr_value, AgentElement):
                        if attr_value.id == id:
                            return attr_value
        for service in self.service_store.values():
            for attr_name, attr_value in vars(service).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    if attr_value.id == id:
                        return attr_value
            # special case for statemachine services, look into nodes
            if isinstance(service, StatemachineService):
                for node in service.nodes.values():
                    if cast(Node, node).id == id:
                        return node
        return None
    
    def is_running(self) -> bool:
        """Check if the Agent is currently running.
        
        Returns:
            bool: True if the Agent is running, False otherwise.
        """
        return self._is_running
     