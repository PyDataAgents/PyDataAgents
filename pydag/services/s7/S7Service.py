from dataclasses import dataclass, field
import snap7
from snap7.type import Areas


from ..ServiceException import ServiceException
from ...agents.Agent import Agent
from ..ReadService import ReadService
from ..WriteService import WriteService
from ...buffers.DataType import DataType

@dataclass
class S7Service(ReadService, WriteService):
    """`Adapter`reading from and writing to S7 PLCs.
    """

    host : str = field(default="127.0.0.1", metadata={"description": "The IP address or hostname of the S7 PLC."})
    rack : int = field(default=0, metadata={"description": "The rack number of the S7 PLC."})
    slot : int = field(default=1, metadata={"description": "The slot number of the S7 PLC."})
        
    def __post_init__(self):
        super().__post_init__()
        self._client : snap7.client.Client = None  # Placeholder for S7 client initialization
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)       
        self._client = snap7.client.Client()
        self._client.connect(self.host, self.rack, self.slot)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self._client:
            try:
                self._client.disconnect()
                self._client = None
            except Exception as e:
                raise ServiceException(f"Could not disconnect from {self.__class__.__name__}") from e

    def _read_from_source(self):
        if len(self.get_buffers()) == len(self.addresses):
            a = 0
            for buffer in self.get_buffers().values():
                address = self.addresses[a]
                d_address = S7Service.address_to_dict(address)
                if "db" in d_address and "s" in d_address and "b" in d_address:
                    db = d_address["db"]
                    s = d_address["s"]
                    b = d_address["b"]
                    data = self._client.read_area(Areas.DB, db, s, b)
                    dt = buffer.data_type()
                    match dt:
                        case DataType.BOOL.value:
                            val = snap7.util.get_bool(data, 0, 0)
                        case DataType.INT.value:
                            val = snap7.util.get_int(data, 0)
                        case DataType.FLOAT.value:
                            val = snap7.util.get_real(data, 0)
                        case DataType.STRING.value:
                            val = snap7.util.get_string(data, 0)
                        case DataType.BYTE.value:
                            val = snap7.util.get_byte(data, 0)
                    buffer.push(val)
                else:
                    raise ServiceException("Invalid address format for S7 PLC: " + address)
                a += 1
        else:
            raise ServiceException("Number of buffers and addresses do not match.")

    def _write_to_sink(self):
        if len(self.get_buffers()) == len(self.addresses):
            a = 0
            for buffer in self.get_buffers().values():
                address = self.addresses[a]
                d_address = S7Service.address_to_dict(address)
                if "db" in d_address and "s" in d_address and "b" in d_address:
                    db = d_address["db"]
                    s = d_address["s"]
                    b = d_address["b"]
                    data = bytearray(b)
                    dt = buffer.data_type()
                    val = data = buffer.data(n=self.n, persistent=self.persistent)
                    match dt:
                        case DataType.BOOL.value:
                            snap7.util.set_bool(data, 0, 0, val)
                        case DataType.INT.value:
                            snap7.util.set_int(data, 0, val)
                        case DataType.FLOAT.value:
                            snap7.util.set_real(data, 0, val)
                        case DataType.STRING.value:
                            snap7.util.set_string(data, 0, val)
                        case DataType.BYTE.value:
                            snap7.util.set_byte(data, 0, val)
                    self._client.write_area(Areas.DB, db, s, data)
                else:
                    raise ServiceException("Invalid address format for S7 PLC: " + address)
                a += 1
        else:
            raise ServiceException("Number of buffers and addresses do not match.")