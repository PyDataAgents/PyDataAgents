from dataclasses import dataclass, field
import pyads
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer


@dataclass
class AdsAdapter(ReadAdapter, WriteAdapter):
    
    ams_net_id : str = field(default=None, metadata = {"description": "AMS Net Id to connect to for ADS Connection"})
    twincat : int = field(default=3, metadata = {"description": "Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3"})
    
    def __init__(self):
        super().__init__()
        self.ads_client : pyads.Connection = None
    
    def connect(self) -> bool:
        match self.twincat:
            case 2:
                self.ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC2PLC1)
            case 3:
                self.ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_TC3PLC1)
        self.ads_client.open()
        print(self.ads_client.read_state())
        return True
    
    def disconnect(self):
        self.ads_client.close()
        self.ads_client = None
        return True
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            val = self.ads_client.read_by_name(addresses[b])
            buffers[key].push(val)
        
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1, persistent : bool = True):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            val = buffers[key].data(n, persistent) 
            if len(val) > 1:
                # TODO
                raise AdapterException("writing more than one value is not supported yet")
            else:
                self.ads_client.write_by_name(addresses[b], val[0])