from abc import abstractmethod
from dataclasses import dataclass, field
import re
import struct

from ...buffers.Buffer import Buffer
from ..ReadAdapter import ReadAdapter
from ..WriteAdapter import WriteAdapter

SCHEMA_SIZES = {
    'i': 4,  # int
    'f': 4,  # float
    'd': 8,  # double
    's': 1,  # char (string of length 1)
    'b': 1,  # byte
    'h': 2,  # short
    'H': 2,  # unsigned short
    'I': 4,  # unsigned int
    'B': 1,  # unsigned byte
    # add more if needed
}

# Type mapping to struct format codes
BYTES_MAP = {
    "uint8": "B",
    "int8": "b",
    "uint16": "H",
    "int16": "h",
    "uint32": "I",
    "int32": "i",
    "float32": "f",
    "float64": "d",
    "string": "s"
}

@dataclass
class ByteStreamAdapter(ReadAdapter, WriteAdapter):
    """
    `Adapter` to read and write byte streams from/to a socket connection.
    The adapter can be configured with different byte schemas for connecting, disconnecting,
    sending, and receiving data.
    the bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5
    """
    
    host : str = field(default=None, metadata={"description": "name of the host to connect to, e.g. IP address or COM-Port"})
    port : int = field(default=None, metadata={"description": "port of the host to connect to"})
    connect_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each connection"})
    disconnect_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each disconnection"})
    send_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each send"})
    before_receive_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each receive"})
    after_receive_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each receive"})
    read_byte_schema : str = field(default=None, metadata={"description": "schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float)"})
    write_byte_schema : str = field(default=None, metadata={"description": "schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10)"})
    data_size : int = field(default=0, metadata={"description": "size of the data to expect when reiceiving bytes"})
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
        pass
    
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0, persistent : bool = True):
        pass
    
    @abstractmethod
    def send(self, data : bytes):
        """
        method to send bytes
        """
        
    @abstractmethod
    def receive(self) -> bytes:
        """
        method to receive bytes
        """
        
    @staticmethod
    def schema_to_bytes(schema : str):
        total = 0
        # pattern: letter optionally followed by digits
        for match in re.finditer(r'([a-zA-Z])(\d*)', schema):
            type_char, count_str = match.groups()
            if type_char == 's':  # string
                if not count_str:
                    raise ValueError("String type 's' must have a length, e.g., s20")
                total += int(count_str)  # string length in bytes
            else:
                size = SCHEMA_SIZES.get(type_char)
                if size is None:
                    raise ValueError(f"Unknown type {type_char}")
                count = int(count_str) if count_str else 1
                total += size * count
        return total
    
    def encode(self, schema : str, data : list) -> bytes:
        """
        encodes data according to the schema
        """
        values = struct.pack(schema, data)
        return values
    
    def decode(self, schema : str, data : bytes) -> list:
        """
        decodes data according to the schema
        """
        values = struct.unpack(schema, data)
        return list(values)
