from dataclasses import dataclass
import socket

from .ByteStreamAdapter import ByteStreamAdapter

@dataclass
class TCPClientAdapter(ByteStreamAdapter):
    
    def __post_init__(self):
        super().__post_init__()
        self.socket : socket.socket = None
    
    def connect(self) -> bool:
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.socket.connect((self.host, self.port))
        if self.connect_bytes is not None:
            self._send(self.connect_bytes)
        return True
    
    def disconnect(self) -> bool:
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        return True
    
    def _send(self, data : bytes):
        """
        method to send bytes
        """
        if self.before_send_bytes is not None:
            self.socket.sendall(self.before_send_bytes)
        self.socket.sendall(data)
        if self.after_send_bytes is not None:
            self.socket.sendall(self.after_send_bytes)
        
    def _receive(self, n : int) -> bytes:
        """
        method to receive bytes
        """
        if self.before_receive_bytes is not None:
            self.socket.sendall(self.before_receive_bytes)
        data = self.socket.recv(n)
        if self.after_receive_bytes is not None:
            self.socket.sendall(self.after_receive_bytes)
        return data
