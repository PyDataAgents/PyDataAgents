from dataclasses import dataclass, field
import snap7
from snap7.type import Areas
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer
from ...buffers.DataType import DataType
from ...utils.AdapterUtils import AdapterUtils

@dataclass
class S7Adapter(ReadAdapter, WriteAdapter):
    """`Adapter`reading from and writing to S7 PLCs.
    """

    host : str = field(default="127.0.0.1", metadata={"description": "The IP address or hostname of the S7 PLC."})
    rack : int = field(default=0, metadata={"description": "The rack number of the S7 PLC."})
    slot : int = field(default=1, metadata={"description": "The slot number of the S7 PLC."})
        
    def __init__(self):
        super().__init__()
        self.client : snap7.client.Client = None  # Placeholder for S7 client initialization

    def connect(self) -> bool:
        self.client = snap7.client.Client()
        self.client.connect(self.host, self.rack, self.slot)
        return True

    def disconnect(self) -> bool:
        self.client.disconnect()
        self.client = None
        return True

    def read_from_source(self, buffers: dict[str, Buffer], addresses: list[str], n: int):
        if len(buffers) == len(addresses):
            a = 0
            for buffer in buffers.values():
                address = addresses[a]
                d_address = AdapterUtils.address_to_dict(address)
                if "db" in d_address and "s" in d_address and "b" in d_address:
                    db = d_address["db"]
                    s = d_address["s"]
                    b = d_address["b"]
                    data = self.client.read_area(Areas.DB, db, s, b)
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
                    raise AdapterException("Invalid address format for S7 PLC: " + address)
                a += 1
        else:
            raise AdapterException("Number of buffers and addresses do not match.")

    def write_to_sink(self, buffers: dict[str, Buffer], addresses: list[str], n : int, persistent: bool = True):
        if len(buffers) == len(addresses):
            a = 0
            for buffer in buffers.values():
                address = addresses[a]
                d_address = AdapterUtils.address_to_dict(address)
                if "db" in d_address and "s" in d_address and "b" in d_address:
                    db = d_address["db"]
                    s = d_address["s"]
                    b = d_address["b"]
                    data = bytearray(b)
                    dt = buffer.data_type()
                    val = data = buffer.data(n, persistent)
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
                    self.client.write_area(Areas.DB, db, s, data)
                else:
                    raise AdapterException("Invalid address format for S7 PLC: " + address)
                a += 1
        else:
            raise AdapterException("Number of buffers and addresses do not match.")