from dataclasses import dataclass
import socket


from ...agents.Agent import Agent
from .ByteStreamService import ByteStreamService

@dataclass
class TCPClientService(ByteStreamService):
    
    def __post_init__(self):
        super().__post_init__()
        self._socket : socket.socket = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # Create a TCP/IP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self._socket.connect((self.host, self.port))
        if self.connect_bytes is not None:
            self._send(self.connect_bytes)
                
    def _on_uninstall(self, agent : Agent = None):
        self._socket = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None
    
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
