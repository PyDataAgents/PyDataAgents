from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.adapters.AdapterException import AdapterException
from PyDataGrabber.src.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.src.adapters.WriteAdapter import WriteAdapter

from opcua import Client

class OpcUaAdapter(ReadAdapter, WriteAdapter):
    
    def __init__(self, id):
        super().__init__(id)
        self.opc_client = None
        
    def endpoint(self, endpoint=None):
        self.endpoint = endpoint
        return self
    
    def connect(self) -> bool:
        self.opc_client = Client(self.endpoint)
        self.opc_client.connect()
        root = self.opc_client.get_root_node()
        print("Object node is: ", root)
        return True
    
    def disconnect(self):
        self.opc_client.disconnect()
        self.opc_client = None
        return True
    
    def readFromSource(self, buffers, addresses):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            node = self.opc_client.get_node(addresses[b])
            val = node.get_value()
            buffers[key].push(val)
        
    def writeToSink(self, buffers, addresses, persistent):
        pass
    
    def config_options(self) -> dict:
        d = super().config_options()
        d["endpoint"] = self.endpoint
        return d
    