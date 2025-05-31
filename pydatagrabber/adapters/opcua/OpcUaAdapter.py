from dataclasses import dataclass, field
from opcua import Client
from PyDataGrabber.pydatagrabber.adapters.AdapterException import AdapterException
from PyDataGrabber.pydatagrabber.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.pydatagrabber.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.pydatagrabber.buffers.Buffer import Buffer

@dataclass
class OpcUaAdapter(ReadAdapter, WriteAdapter):
    
    endpoint : str = field(default=None, metadata={"description" : "endpoint of the opc ua server, e.g. opc.tcp://localhost:48010"})
    
    def __init__(self):
        super().__init__()
        self.opc_client : Client = None
    
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
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        if n == 1:
            for key in buffers:
                node = self.opc_client.get_node(addresses[b])
                val = node.get_value()
                buffers[key].push(val)
        else:
            raise AdapterException("read_from_source is not implemented for n > 1")
        
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1, persistent : bool = False):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            node = self.opc_client.get_node(addresses[b])
            val = buffers[key].data(n = n, persistent=persistent)
            self.opc_client.set_values(node, val)
    