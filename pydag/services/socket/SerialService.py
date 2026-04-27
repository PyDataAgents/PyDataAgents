from dataclasses import dataclass, field
import serial


from ..ServiceException import ServiceException
from ...agents.Agent import Agent
from .ByteStreamService import ByteStreamService


@dataclass
class SerialService(ByteStreamService):
    """ `ByteStreamService` for serial communication using pySerial.
    """
    
    baud_rate : int = field(default=9600, metadata={"description": "baud rate for serial communication"})
    new_line_mode : bool = field(default=True, metadata={"description": "whether to use new line mode for parsing serial communication"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use in new line mode"})
    
    def __post_init__(self):
        super().__post_init__()
        self._serial = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install()
        self._serial = serial.Serial(
            port=self.host,
            baudrate=self.baud_rate,
            timeout=self.timeout
        )
        if self.connect_bytes is not None:
            self._send(self.connect_bytes)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self.disconnect_bytes is not None:
            self._send(self.disconnect_bytes)
        if self._serial:
            try:
                self._serial.close()
            except Exception as e:
                raise ServiceException(f"could not disconnect from serial stream in {self.__class__.__name__}") from e       
        
    def _send(self, data: bytes):
        if self.before_send_bytes is not None:
            self._serial.write(self.before_send_bytes)
        self._serial.write(data)
        if self.after_send_bytes is not None:
            self._serial.write(self.after_send_bytes)
    
    def _receive(self, n: int) -> bytes:
        if self.before_receive_bytes is not None:
            self._serial.write(self.before_receive_bytes)
        bs : bytes = None
        if self.new_line_mode:           
            if n > 0:
                ba = bytearray()
                for _ in range(n):
                    line = self._serial.readline().decode('utf-8').strip()
                    tu = zip(line.split(self.delimiter))
                    tu_forced = ByteStreamService.force_schema(self.read_byte_schema, tu)
                    ba.extend(self._encode(self.read_byte_schema, tu_forced))
                bs = bytes(ba)
            else:
                line = self._serial.readline().decode('utf-8').strip()                
                tu = zip(line.split(self.delimiter))
                tu_forced = ByteStreamService.force_schema(self.read_byte_schema, tu)
                bs = self._encode(self.read_byte_schema, tu_forced)
        else:
            bs = self._serial.read(n)
        if self.after_receive_bytes is not None:
            self._serial.write(self.after_receive_bytes)
        return bs
    
