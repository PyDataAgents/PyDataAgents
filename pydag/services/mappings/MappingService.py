from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from loguru import logger


from ...services.ThreadType import ThreadType
from ...services.ServiceException import ServiceException
from ...adapters.Adapter import Adapter
from ...buffers.Buffer import Buffer
from .MappingObserver import MappingObserver
from .MappingType import MappingType
from ..ObserverThread import ObserverThread
from .PublishMappingObserver import PublishMappingObserver
from .ReadMappingObserver import ReadMappingObserver
from .SubscribeMappingObserver import SubscribeMappingObserver
from .WriteMappingObserver import WriteMappingObserver
from ...services.ObserverService import ObserverService
from ...adapters.WriteAdapter import WriteAdapter
from ...adapters.SubscribeAdapter import SubscribeAdapter
from ...adapters.PublishAdapter import PublishAdapter
from ...adapters.ReadAdapter import ReadAdapter

if TYPE_CHECKING:
    from pydag.agents.Agent import Agent

@dataclass
class MappingService(ObserverService):
    """A `ObserverService` for mapping `Adapter`s and `Buffer`s together for reading, writing, subscribing or publishing from sources and sinks

    Raises:
        ServiceException: _description_

    Returns:
        _type_: _description_
    """
    
    buffer_ids : list[str] = field(default_factory=list, metadata={"description": "list of buffer ids to map from"})
    adapter_id : str = field(default=None, metadata={"description": "id of the Adapter used for this Mapping"})
    addresses : list[str] = field(default_factory=list, metadata={"description": "list of addresses to read/subscribe from or write/publish to"})
    mapping_type : str = field(default=None, metadata={"description": "type of mapping, e.g. READ, WRITE, SUB or PUB"})
    n : int = field(default=1, metadata={"description": "number of samples to insert or remove from buffers"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink"})
    
    def __post_init__(self):
        super().__post_init__()
        self._buffers : dict[str, Buffer] = dict()
        self._adapter : Adapter = None
        
    def _on_install(self, agent : Agent = None):
        # assemble adapters and buffers from agent
        if self._adapter is None:
            if agent is not None:                        
                if agent.get_adapter(self.adapter_id):
                    self._adapter = agent.get_adapter(self.adapter_id)
                else:
                    logger.error("Adapter " + self.adapter_id + " not found in agent")
            else:
                logger.error("Agent is None, cannot get adapter " + self.adapter_id)
        if len(self._buffers) == 0:
            if agent is not None:
                for buffer_id in self.buffer_ids:
                        if buffer_id in agent.get_buffer(buffer_id):
                            self.add_buffer(agent.get_buffer(buffer_id))
                        else:
                            logger.error("Buffer " + buffer_id + " not found in agent")
            else:
                logger.error("Agent is None, cannot get buffers " + str(self.buffer_ids))
        # check auto complete for mapping_type and thread type
        match self.mapping_type:
            case MappingType.READ:
                if not issubclass(self._adapter.__class__, ReadAdapter):
                    raise ServiceException("adapter must be of type " + ReadAdapter.__name__)
            case MappingType.WRITE:
                if not issubclass(self._adapter.__class__, WriteAdapter):
                    raise ServiceException("adapter must be of type " + WriteAdapter.__name__)
            case MappingType.SUB:
                if not issubclass(self._adapter.__class__, SubscribeAdapter):
                    raise ServiceException("adapter must be of type " + SubscribeAdapter.__name__) 
                if self.thread_type is None:                    
                    self.thread_type = ThreadType.ONLY_ONCE.value
                    logger.debug(f"auto-completed thread_type to {self.thread_type}")
            case MappingType.PUB:
                if not issubclass(self._adapter.__class__, PublishAdapter):
                    raise ServiceException("adapter must be of type " + PublishAdapter.__name__)
                if self.thread_type is None:                    
                    self.thread_type = ThreadType.ONLY_ONCE.value
                    logger.debug(f"auto-completed thread_type to {self.thread_type}")             
            case None:
                # try to detect correct mapping type
                if issubclass(self._adapter.__class__, ReadAdapter):
                    if not issubclass(self._adapter.__class__, WriteAdapter):
                        if not issubclass(self._adapter.__class__, SubscribeAdapter):
                            if not issubclass(self._adapter.__class__, PublishAdapter):
                                self.mapping_type = MappingType.READ.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                elif issubclass(self._adapter.__class__, WriteAdapter):
                    if not issubclass(self._adapter.__class__, ReadAdapter):
                        if not issubclass(self._adapter.__class__, SubscribeAdapter):
                            if not issubclass(self._adapter.__class__, PublishAdapter):
                                self.mapping_type = MappingType.WRITE.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                elif issubclass(self._adapter.__class__, SubscribeAdapter):
                    if not issubclass(self._adapter.__class__, ReadAdapter):
                        if not issubclass(self._adapter.__class__, WriteAdapter):
                            if not issubclass(self._adapter.__class__, PublishAdapter):
                                self.mapping_type = MappingType.SUB.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                                if self.thread_type is None:                    
                                    self.thread_type = ThreadType.ONLY_ONCE.value
                                    logger.debug(f"auto-completed thread_type to {self.thread_type}")
                elif issubclass(self._adapter.__class__, PublishAdapter):
                    if not issubclass(self._adapter.__class__, ReadAdapter):
                        if not issubclass(self._adapter.__class__, WriteAdapter):
                            if not issubclass(self._adapter.__class__, SubscribeAdapter):
                                self.mapping_type = MappingType.PUB.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                                if self.thread_type is None:                    
                                    self.thread_type = ThreadType.ONLY_ONCE.value
                                    logger.debug(f"auto-completed thread_type to {self.thread_type}")
        # check if mapping_type and thread_type are still not set
        if self.mapping_type is None:
            raise ServiceException("could not detect mapping_type, please set it explicitly")
        if self.thread_type is None:
            raise ServiceException("could not detect thread_type, please set it explicitly")
        
        # create observer based on mapping
        observer : MappingObserver = None
        match self.mapping_type:
            case MappingType.READ:
                observer = ReadMappingObserver(self)
            case MappingType.WRITE:
                observer = WriteMappingObserver(self)
            case MappingType.SUB:
                observer = SubscribeMappingObserver(self)
            case MappingType.PUB:
                observer = PublishMappingObserver(self)

        super()._on_install(agent)
        self._observer_thread.add_observer(observer)        
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._buffers : dict[str, Buffer] = dict()
        self._adapter : Adapter = None
            
    def get_observer_thread(self) -> ObserverThread:
        return self._observer_thread
    
    def set_adapter(self, adapter : Adapter):
        """ set the `Adapter` of this `MappingService`

        Args:
            adapter (Adapter): `Adapter` instance
        """
        self._adapter = adapter
        self.adapter_id = adapter.id
        
    def set_buffers(self, buffers : dict[str, 'Buffer']):
        """ set the `Buffer`s of this `MappingService`

        Args:
            buffers (dict[str, Buffer]): dictionary of `Buffer`s
        """
        self._buffers = buffers
        self.buffer_ids = buffers.keys()
        
    def add_buffer(self, buffer : 'Buffer'):
        """ add a `Buffer` to this `MappingService`

        Args:
            buffer (Buffer): instance of `Buffer`
        """
        self._buffers[buffer.id] = buffer
        if buffer.id not in self.buffer_ids:
            self.buffer_ids.append(buffer.id)
            
    def get_adapter(self) -> Adapter:
        """ return this `MappingService`'s `Adapter`

        Returns:
            Adapter: instance of `Adapter`
        """
        return self._adapter
    
    def get_buffers(self) -> dict[str, 'Buffer']:
        """ returns this `MappingService`'s `Buffer`s

        Returns:
            dict[str, Buffer]: dictionary of buffers
        """
        return self._buffers
        