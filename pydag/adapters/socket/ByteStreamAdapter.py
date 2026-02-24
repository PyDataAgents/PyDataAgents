from abc import abstractmethod
from dataclasses import dataclass, field
import re
import struct
from typing import Union

from ...adapters.AdapterException import AdapterException
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
    <br>The adapter can be configured with different byte schemas for connecting, disconnecting,
    sending, and receiving data.
    <br>The bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5
    <br>The addresses in read_from_source and write_to_sink are used to specify the buffer keys to read from or write to.
    <br>e.g. addresses = ["B1", "B3", "SENSOR1"]
    <br>The length of the addresses list must not match the number of buffers passed, all buffers are being searched for the keys in addresses.
    But it has to match the number of elements in the schema used for reading or writing. Omiting schema fields can be done by specifying None in the addresses list.
    <br>For Example:
    <br>schema = "BfI" -> addresses = ["ID1", None, "ID3"]
    """
    
    host : str = field(default=None, metadata={"description": "name of the host to connect to, e.g. IP address or COM-Port"})
    port : int = field(default=None, metadata={"description": "port of the host to connect to, in case of Serial Protocol this is ignored"})
    timeout : int = field(default=1, metadata={"description": "timeout in seconds for connecting to the host"})
    connect_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each connection"})
    disconnect_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each disconnection"})
    before_send_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each send"})
    after_send_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each send"})
    before_receive_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each receive"})
    after_receive_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each receive"})
    read_byte_schema : str = field(default=None, metadata={"description": "schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float)"})
    write_byte_schema : str = field(default=None, metadata={"description": "schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10)"})
    
        
    def _on_read(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
        b, f = ByteStreamAdapter.decode_schema(self.read_byte_schema)
        read_bytes = self._receive(b * (n if n > 0 else 1))
        data_tuples = self._decode(self.read_byte_schema, read_bytes)
        if len(addresses) == 0:
            if len(buffers) == 1:
                buffer = next(iter(buffers.values()))    
                for data in data_tuples:
                    dic = {}
                    for i, value in enumerate(data):
                        dic[f"field_{i}"] = value
                    buffer.push(dic)
            else:
                tn = next(iter(data_tuples))
                if len(buffers) != len(tn):
                    raise AdapterException("Number of buffers does not match number of data fields")
                for data in data_tuples:
                    b = 0
                    for buffer in buffers.values():
                        buffer.push({f"field_{i}": data[b]})
        else:
            tn = next(iter(data_tuples))
            if len(addresses) != len(tn):
                raise AdapterException("Number of addresses does not match number of data fields")             
            if len(buffers) == 1:
                buffer = next(iter(buffers.values()))
                for data in data_tuples:
                    dic = {}
                    for i, address in enumerate(addresses):
                        if address is not None:
                            dic[address] = data[i]
                    buffer.push(dic)
            else:
                success = False
                for data in data_tuples:
                    addr_idx = 0
                    for address in addresses:
                        if address is not None:
                            for buffer in buffers.values():
                                if address in buffer.data().keys():
                                    buffer.push({address: data[addr_idx]})
                                    success = True
                        addr_idx += 1
                if not success:
                    raise AdapterException("No matching addresses found in buffers")                

    def _on_write(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0, persistent : bool = True):
        if len(addresses) == 0:
            if len(buffers) == 1:
                buffer = next(iter(buffers.values()))    
                d = buffer.data(n = n, persistent = persistent)
                data_lists = []
                b, f = ByteStreamAdapter.decode_schema(self.write_byte_schema)
                if len(d.keys()) == f:
                    for key in d.keys():
                        data_lists.append(d[key])
                    # prepare as list of tuples
                    data_tuples = list(zip(*data_lists))
                    encoded_bytes = self._encode(self.write_byte_schema, data_tuples)
                    self._send(encoded_bytes)
                else:
                    raise AdapterException("Number of buffer keys does not match number of schema fields")
            else:
                data_lists = []
                for buffer in buffers.values():
                    d = buffer.data(n = n, persistent = persistent)
                    for key in d.keys():
                        data_lists.append(d[key])
                # prepare as list of tuples
                data_tuples = list(zip(*data_lists))
                encoded_bytes = self._encode(self.write_byte_schema, data_tuples)
                self._send(encoded_bytes)
        else:
            data_lists = []
            for buffer in buffers.values():
                for address in addresses:
                    d = buffer.data(n = n, persistent = persistent)
                    if address in buffer.data().keys():
                        data_lists.append(d[address])
            # prepare as list of tuples
            data_tuples = list(zip(*data_lists))
            encoded_bytes = self._encode(self.write_byte_schema, data_tuples)
            self._send(encoded_bytes)
    
    @abstractmethod
    def _send(self, data : bytes):
        """
        method to send bytes
        """
        
    @abstractmethod
    def _receive(self, n : int) -> bytes:
        """
        method to receive `n` number of bytes
        """
        
    @staticmethod
    def decode_schema(schema : str) -> tuple[int, int]:
        """ returns the number of bytes and schema fields

        Args:
            schema (str): schema string, e.g. "BfI"

        Raises:
            AdapterException: if incorrect schema or unknown type is found

        Returns:
            tuple[int, int]: number of bytes, number of fields
        """
        b = 0
        m = 0
        # pattern: letter optionally followed by digits
        matches = re.findall(r'(\d*)([a-zA-Z])', schema)
        for match in matches:
            f = "=" + "".join(match)
            size = struct.calcsize(f)
            b += size
            m += 1
        return b, m
    
    @staticmethod
    def force_schema(schema : str, data : Union[tuple | list[tuple]]) ->  Union[tuple | list[tuple]]:
        """ forces the data to match the schema by converting types

        Args:
            schema (str): schema string, e.g. "BfI"
            data (Union[tuple, list[tuple]]): data to convert

        Raises:
            AdapterException: if data cannot be converted to schema types

        Returns:
            Union[tuple, list[tuple]]: converted data
        """
        def convert_value(value, fmt):
            if fmt in ['b', 'B', 'h', 'H', 'i', 'I']:
                return int(value)
            elif fmt in ['f', 'd']:
                return float(value)
            elif fmt.endswith('s'):
                length = int(fmt[:-1]) if fmt[:-1].isdigit() else 1
                str_value = str(value)
                if len(str_value) > length:
                    return str_value[:length].encode('utf-8')
                else:
                    return str_value.ljust(length, '\x00').encode('utf-8')
            else:
                raise AdapterException(f"Unknown format code: {fmt}")

        matches = re.findall(r'(\d*)([a-zA-Z])', schema)
        formats = ["".join(match) for match in matches]

        if isinstance(data, tuple):
            if len(data) != len(formats):
                raise AdapterException("Data length does not match schema length")
            return tuple(convert_value(data[i], formats[i]) for i in range(len(data)))
        elif isinstance(data, list):
            converted_list = []
            for item in data:
                if len(item) != len(formats):
                    raise AdapterException("Data item length does not match schema length")
                converted_item = tuple(convert_value(item[i], formats[i]) for i in range(len(item)))
                converted_list.append(converted_item)
            return converted_list
        else:
            raise AdapterException("Data must be a tuple or list of tuples")
    
    def _encode(self, schema : str, data : Union[tuple | list[tuple]]) -> bytes:
        """
        encodes data according to the schema
        """
        if isinstance(data, tuple):
            bytes_obj = struct.pack(schema, *data)
            return bytes_obj
        elif isinstance(data, list):
            bytes_ar = bytearray()
            for item in data:
                if isinstance(item, tuple):
                    bytes_ar += struct.pack(schema, *item)
                else:
                    raise AdapterException("Data items must be tuples when data is a list")
            return bytes(bytes_ar)
    
    def _decode(self, schema : str, data : bytes) -> list[tuple]:
        """
        decodes data according to the schema
        """
        sb, fn = ByteStreamAdapter.decode_schema(schema)
        if len(data) != sb:
            if len(data) % sb == 0:
                values = [
                    struct.unpack(schema, data[i : i + sb])
                    for i in range(0, len(data), sb)
                ]
                return values
            else:
                raise AdapterException(f"Data length {len(data)} does not match schema size {sb}")
        else:
            values = struct.unpack(schema, data)
            return list(values)
