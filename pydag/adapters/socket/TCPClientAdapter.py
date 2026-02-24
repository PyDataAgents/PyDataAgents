from dataclasses import dataclass
import socket


from ...agents.Agent import Agent
from .ByteStreamAdapter import ByteStreamAdapter

@dataclass
class TCPClientAdapter(ByteStreamAdapter):
    
    def __post_init__(self):
        super().__post_init__()
        self._socket : socket.socket = None
    
    def _on_install(self, agent : Agent = None):
        # Create a TCP/IP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
    def _on_uninstall(self, agent : Agent = None):
        self._socket = None
    
    def _on_connect(self) -> bool:
        # Connect to the server
        self._socket.connect((self.host, self.port))
        if self.connect_bytes is not None:
            self._send(self.connect_bytes)
        return True

    def _on_disconnect(self) -> bool:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        return True
    
    def _send(self, data : bytes):
        """
        method to send bytes
        """
        if self.before_send_bytes is not None:
            self._socket.sendall(self.before_send_bytes)
        self._socket.sendall(data)
        if self.after_send_bytes is not None:
            self._socket.sendall(self.after_send_bytes)
        
    def _receive(self, n : int) -> bytes:
        """
        method to receive bytes
        """
        if self.before_receive_bytes is not None:
            self._socket.sendall(self.before_receive_bytes)
        data = self._socket.recv(n)
        if self.after_receive_bytes is not None:
            self._socket.sendall(self.after_receive_bytes)
        return data
