from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from loguru import logger


from .ThreadType import ThreadType
from ..utils.StringUtils import StringUtils
from .Service import Service
from .ServiceException import ServiceException
from ..buffers.Buffer import Buffer
from .MappingObserver import MappingObserver
from .MappingType import MappingType
from .PublishMappingObserver import PublishMappingObserver
from .ReadMappingObserver import ReadMappingObserver
from .SubscribeMappingObserver import SubscribeMappingObserver
from .WriteMappingObserver import WriteMappingObserver
from .ObserverService import ObserverService

if TYPE_CHECKING:
    from pydag.agents.Agent import Agent


@dataclass
class MappingService(ObserverService):
    """A `ObserverService` for mapping `Buffer`s together for reading, writing, subscribing or publishing from sources and sinks

    Raises:
        ServiceException: _description_

    Returns:
        _type_: _description_
    """
    
    buffer_ids : list[str] = field(default_factory=list, metadata={"description": "list of buffer ids to map from"})
    addresses : list[str] = field(default_factory=list, metadata={"description": "list of addresses to read/subscribe from or write/publish to"})
    mapping_type : str = field(default=None, metadata={"description": "type of mapping, e.g. READ, WRITE, SUB or PUB"})
    n : int = field(default=0, metadata={"description": "number of samples to insert or remove from buffers"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink"})
    
    def __post_init__(self):
        super().__post_init__()
        self._buffers : dict[str, Buffer] = dict()
        
    def _on_install(self, agent : Agent = None):        
        from .PublishService import PublishService
        from .SubscribeService import SubscribeService
        from .WriteService import WriteService
        from .ReadService import ReadService
        # assemble buffers from agent
        if len(self._buffers) == 0:
            if agent is not None:
                for buffer_id in self.buffer_ids:
                    buffer : Buffer = agent.get_buffer(buffer_id)
                    if buffer:
                        self.add_buffer(buffer)
                    else:
                        logger.error("Buffer " + buffer_id + " not found in agent")
            else:
                logger.error("Agent is None, cannot get buffers " + str(self.buffer_ids))
        # check auto complete for mapping_type and thread type
        match self.mapping_type:
            case MappingType.READ:                
                if not issubclass(self.__class__, ReadService):
                    raise ServiceException(f"{Service.__name__} must be of type {ReadService.__name__}")
            case MappingType.WRITE:
                if not issubclass(self.__class__, WriteService):
                    raise ServiceException(f"{Service.__name__} must be of type {WriteService.__name__}")
            case MappingType.SUB:
                self.thread_type = ThreadType.DAEMON.value
                if not issubclass(self.__class__, SubscribeService):
                    raise ServiceException(f"{Service.__name__} must be of type {SubscribeService.__name__}")
            case MappingType.PUB:
                self.thread_type = ThreadType.DAEMON.value
                if not issubclass(self.__class__, PublishService):
                    raise ServiceException(f"{Service.__name__} must be of type {PublishService.__name__}")            
            case None:
                # try to detect correct mapping type
                if issubclass(self.__class__, ReadService):
                    if not issubclass(self.__class__, WriteService):
                        if not issubclass(self.__class__, SubscribeService):
                            if not issubclass(self.__class__, PublishService):
                                self.mapping_type = MappingType.READ.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                elif issubclass(self.__class__, WriteService):
                    if not issubclass(self.__class__, ReadService):
                        if not issubclass(self.__class__, SubscribeService):
                            if not issubclass(self.__class__, PublishService):
                                self.mapping_type = MappingType.WRITE.value
                                logger.debug(f"auto-completed mapping_type to {self.mapping_type} in {self.config_options()}")
                elif issubclass(self.__class__, SubscribeService):
                    if not issubclass(self.__class__, ReadService):
                        if not issubclass(self.__class__, WriteService):
                            if not issubclass(self.__class__, PublishService):
                                self.mapping_type = MappingType.SUB.value
                                self.thread_type = ThreadType.DAEMON.value
                                logger.debug(f"auto-completed mapping_type and thread_ype to {self.mapping_type} and {self.thread_type} in {self.config_options()}")
                elif issubclass(self.__class__, PublishService):
                    if not issubclass(self.__class__, ReadService):
                        if not issubclass(self.__class__, WriteService):
                            if not issubclass(self.__class__, SubscribeService):
                                self.mapping_type = MappingType.PUB.value
                                self.thread_type = ThreadType.DAEMON.value
                                logger.debug(f"auto-completed mapping_type and thread_ype to {self.mapping_type} and {self.thread_type} in {self.config_options()}")
        # check if mapping_type and thread_type are still not set
        if self.mapping_type is None:
            raise ServiceException("could not detect mapping_type, please set it explicitly")
        if self.thread_type is None:
            raise ServiceException("could not detect thread_type, please set it explicitly")
        
        super()._on_install(agent)
         
        # create observer based on mapping
        observer : MappingObserver = None
        match self.mapping_type:
            case MappingType.READ:
                observer = ReadMappingObserver(self)
                self.add_observer(observer)  
            case MappingType.WRITE:
                observer = WriteMappingObserver(self)                
                self.add_observer(observer)  
            case MappingType.SUB:
                observer = SubscribeMappingObserver(self)
                self.add_observer(observer)
            case MappingType.PUB:
                observer = PublishMappingObserver(self)
                self.add_observer(observer)      
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._buffers : dict[str, Buffer] = dict()
            
    def _on_stop(self):
        super()._on_stop()
            
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
    
    def get_buffers(self) -> dict[str, 'Buffer']:
        """ returns this `MappingService`'s `Buffer`s

        Returns:
            dict[str, Buffer]: dictionary of buffers
        """
        return self._buffers
    
    @staticmethod
    def address_to_list(address : str) -> list:
        addresses = []
        addresses.append(address)
        return addresses

    @staticmethod
    def address_to_dict(address : str) -> dict[str, str]:
        d = StringUtils.string_to_dict(address)
        return d
        