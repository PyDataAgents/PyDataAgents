from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Tuple

from ...buffers.Buffer import Buffer
from ..ReadAdapter import ReadAdapter
from ..WriteAdapter import WriteAdapter
from ...buffers.DataType import DataType


@dataclass
class ByteStreamAdapter(ReadAdapter, WriteAdapter):
    
    host : str = field(default=None, metadata={"description": "name of the host to connect to, e.g. IP address or COM-Port"})
    port : int = field(default=None, metadata={"description": "port of the host to connect to"})
    connect_byteschema : list[Tuple[DataType, int]] = field(default_factory=None, metadata={"byteschema for the connection"})
    connect_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each connection"})
    disconnect_byteschema : list[Tuple[DataType, int]] = field(default_factory=None, metadata={"byteschema for the disconnection"})
    disconnect_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each disconnection"})
    send_byteschema : list[Tuple[DataType, int]] = field(default_factory=None, metadata={"byteschema for the sending"})
    send_bytes : bytes = field(default=None, metadata={"description": "bytes to send before each send"})
    receive_byteschema : list[Tuple[DataType, int]] = field(default_factory=None, metadata={"byteschema for the receiving"})
    receive_bytes : bytes = field(default=None, metadata={"description": "bytes to send after each receive"})
    
    def connect(self) -> bool:
        res = self.on_connect()
        if self.connect_byteschema is not None:
            # TODO
            pass
               
    def disconnect(self) -> bool:
        res = self.on_disconnect()
        
        
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
    
    @abstractmethod
    def on_connect(self) -> bool:
        """ method for connecting
        """    
            
    @abstractmethod
    def on_disconnect(self) -> bool:
        """ method for disconnecting
        """
        
