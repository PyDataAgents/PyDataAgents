from dataclasses import dataclass, field
import pyads
from loguru import logger


from ..ServiceException import ServiceException
from ..ReadService import ReadService
from ..WriteService import WriteService
from ...agents.Agent import Agent


@dataclass
class AdsService(ReadService, WriteService):
    """`MappingService` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).
    """
    
    ams_net_id : str = field(default=None, metadata = {"description": "AMS Net Id to connect to for ADS Connection"})
    twincat : int = field(default=3, metadata = {"description": "Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3"})
    
    def __post_init__(self):
        super().__post_init__()
        self._ads_client : pyads.Connection = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install()
        match self.twincat:
            case 2:
                self._ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC2PLC1)
            case 3:
                self._ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC3PLC1)
        try:
            self._ads_client.open()
        except Exception as e:
            logger.error(f"Failed to open ADS connection: {e}")

    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall()
        self._ads_client.close()
        self._ads_client = None
        
    def _read_from_source(self):
        if len(self.get_buffers()) == 1 and len(self.addresses) > 1:
            # if only one buffer is provided, we assume that all addresses should be read into this buffer
            buffer = next(iter(self.get_buffers().values()))
            d : dict = {}
            for address in self.addresses:
                val = self._ads_client.read_by_name(address)
                if val is None:
                    raise ServiceException(f"Reading {address} returned None, {self.__class__.__name__} might be unconnected or invalid address")
                d[address] = val            
            buffer.push(d)
        elif len(self.get_buffers()) != len(self.addresses):
            raise ServiceException("size of buffers and addresses must match")
        else:
            b = 0
            for buffer in self.get_buffers().values():
                val = self._ads_client.read_by_name(self.addresses[b])
                if val is None:
                    raise ServiceException(f"Reading {self.addresses[b]} returned None, {self.__class__.__name__} might be unconnected or invalid address")
                buffer.push(val)
                b = b + 1
        
        
    def _write_to_sink(self):
        if len(self.get_buffers()) != len(self.addresses):
            raise ServiceException("size of buffers and addresses must match")
        b = 0
        for key, buffer in self.get_buffers().items():
            val = buffer.data(n=self.n, persistent=self.persistent) 
            if len(val) > 1:
                # TODO
                raise ServiceException("writing more than one value is not supported yet")
            else:
                self._ads_client.write_by_name(self.addresses[b], val[0])