from dataclasses import dataclass, field
from opcua import Client, Node, ua
from opcua.ua.uaerrors import UaStatusCodeError


from ...buffers.DataType import DataType
from ..BrowsingService import BrowseFilter, BrowsingService, Address
from ...agents import Agent
from ..ReadService import ReadService
from ..WriteService import WriteService
from ..ServiceException import ServiceException


@dataclass
class OpcUaService(ReadService, WriteService, BrowsingService):
    """`MappingService` for reading and writing data from/to OPC UA servers.
    """
    
    endpoint : str = field(default=None, metadata={"description" : "endpoint of the opc ua server, e.g. opc.tcp://localhost:48010"})
    
    def __post_init__(self):
        super().__post_init__()
        self._client : Client = None        
        
    
    def _on_install(self, agent : Agent = None):
        self._client = Client(self.endpoint)
        self._client.connect()
        root : Node = self._client.get_root_node()
        #print("Object node is: ", root)
        if root is None:
            raise ServiceException(f"Connection to OPC UA server failed in {self.__class__.__name__}")
        
    def _on_uninstall(self, agent : Agent = None):      
        self._client = None
        if self._client:
            try:
                self._client.disconnect()
            except Exception as e:
                raise ServiceException(f"Disconnecting from OPC UA server failed in {self.__class__.__name__}") from e
    
    def read_from_source(self):
        if len(self.get_buffers()) != len(self.addresses):
            raise ServiceException("size of buffers and addresses must match")
        b = 0
        if self.n == 1:
            for k, v in self.get_buffers().items():
                node = self._client.get_node(self.addresses[b])
                val = node.get_value()
                v.push(val)
        else:
            raise ServiceException("read_from_source is not implemented for n > 1")
        
    def write_to_sink(self):
        if len(self.get_buffers()) != len(self.addresses):
            raise ServiceException("size of buffers and addresses must match")
        b = 0
        for k, v in self.get_buffers().items():
            node = self._client.get_node(self.addresses[b])
            val = v.data(n = self.n, persistent=self.persistent)
            self._client.set_values(node, val)
            
    def browse(self, browse_filter : BrowseFilter = None) -> list[Address]:
        root : Node = self._client.get_root_node()
        addresses : list[Address] = []
        self._recursive_browse(root, browse_filter, addresses)
        return addresses
        
    def _recursive_browse(self, node : Node, browse_filter : BrowseFilter = None, addresses : list[Address] = None):
        if addresses is None:
            addresses = []
        children = node.get_children()
        child : Node
        for child in children:
            address = f"ns={child.nodeid.NamespaceIndex};i={child.nodeid.Identifier}"
            node_class = child.get_node_class()
            if node_class == ua.NodeClass.Variable:
                datatype_node_id = child.get_data_type()
                datatype_node = self._client.get_node(datatype_node_id)
                datatype_name = datatype_node.get_browse_name().Name
                data_type = OpcUaService._from_opc_datatype(datatype_name)
                try:
                    description = child.get_description().Text
                except UaStatusCodeError:
                    description = None
                addr = Address(source = self.config_options(), address = address, data_type = data_type.value, unit  = None, description = description)
                if browse_filter is None or browse_filter.filter(addr):
                    addresses.append(addr)
            self._recursive_browse(child, browse_filter, addresses)
    
    @staticmethod
    def _from_opc_datatype(opc_datatype: str) -> DataType:
        # Implementation for converting OPC UA datatype to DataType
        match opc_datatype:
            case "Boolean":
                return DataType.BOOL
            case "UInt64":
                return DataType.FLOAT
            case "UInt32":
                return DataType.INT
            case "UInt16":
                return DataType.INT
            case "Int32":
                return DataType.INT
            case "Float":
                return DataType.FLOAT
            case "Double":
                return DataType.FLOAT
            case "String":
                return DataType.STRING
            case "UtcTime":
                return DataType.INT
            case "DateTime":
                return DataType.INT
            case "ByteString":
                return DataType.STRING
            case _:
                return DataType.OBJECT