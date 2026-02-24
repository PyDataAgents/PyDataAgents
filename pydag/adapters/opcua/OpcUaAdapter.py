from dataclasses import dataclass, field
from opcua import Client


from ...agents import Agent
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer

@dataclass
class OpcUaAdapter(ReadAdapter, WriteAdapter):
    """`Adapter` for reading and writing data from/to OPC UA servers.
    """
    
    endpoint : str = field(default=None, metadata={"description" : "endpoint of the opc ua server, e.g. opc.tcp://localhost:48010"})
    
    def __post_init__(self):
        super().__post_init__()
        self._client : Client = None
    
    def _on_install(self, agent : Agent = None):        
        self._client = Client(self.endpoint)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
    
    def _on_connect(self) -> bool:
        self._client.connect()
        root = self._client.get_root_node()
        print("Object node is: ", root)
        return True
    
    def _on_disconnect(self):
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                return False
        self._client = None
        return True

    def _on_read(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        if n == 1:
            for key in buffers:
                node = self._client.get_node(addresses[b])
                val = node.get_value()
                buffers[key].push(val)
        else:
            raise AdapterException("read_from_source is not implemented for n > 1")
        
    def _on_write(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1, persistent : bool = False):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for key in buffers:
            node = self._client.get_node(addresses[b])
            val = buffers[key].data(n = n, persistent=persistent)
            self._client.set_values(node, val)
    