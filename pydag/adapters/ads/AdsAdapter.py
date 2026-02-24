from dataclasses import dataclass, field
import pyads

from ...agents.Agent import Agent
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer


@dataclass
class AdsAdapter(ReadAdapter, WriteAdapter):
    """`Adapter` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).
    """
    
    ams_net_id : str = field(default=None, metadata = {"description": "AMS Net Id to connect to for ADS Connection"})
    twincat : int = field(default=3, metadata = {"description": "Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3"})
    
    def __post_init__(self):
        super().__post_init__()
        self._ads_client : pyads.Connection = None
    
    def _on_install(self, agent : Agent = None):
        match self.twincat:
            case 2:
                self._ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC2PLC1)
            case 3:
                self._ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC3PLC1)
    
    def _on_uninstall(self, agent : Agent = None):
        self._ads_client = None
    
    def _on_connect(self) -> bool:        
        self._ads_client.open()
        print(self._ads_client.read_state())
        return True
    
    def _on_disconnect(self):
        self._ads_client.close()
        
        return True
    
    def _on_read(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            val = self._ads_client.read_by_name(addresses[b])
            buffers[key].push(val)
        
    def _on_write(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1, persistent : bool = True):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            val = buffers[key].data(n, persistent) 
            if len(val) > 1:
                # TODO
                raise AdapterException("writing more than one value is not supported yet")
            else:
                self._ads_client.write_by_name(addresses[b], val[0])