import pyads
from PyDataGrabber.src.adapters.AdapterException import AdapterException
from PyDataGrabber.src.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.src.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.src.buffers.Buffer import Buffer


class AdsAdapter(ReadAdapter, WriteAdapter):
    
    def __init__(self, id):
        super().__init__(id)
        self.ads_client : pyads.Connection = None
        self.ams_net_id : str = None
        
    def connect(self) -> bool:
        self.ads_client = pyads.Connection(self.ams_net_id, pyads.PORT_SPS1)
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
        
    def writeToSink(self, buffers : dict[str, Buffer], addresses : list[str], persistent : bool, n : int = 1):
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
    
    def config_options(self) -> dict:
        d = super().config_options()
        d["ams_net_id"] = self.ams_net_id
        return d