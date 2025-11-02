from dataclasses import dataclass, field
import serial


from ...adapters.socket.ByteStreamAdapter import ByteStreamAdapter


@dataclass
class SerialAdapter(ByteStreamAdapter):
    """ `Adapter` for serial communication using pySerial.
    """
    
    baud_rate : int = field(default=9600, metadata={"description": "baud rate for serial communication"})
    new_line_mode : bool = field(default=True, metadata={"description": "whether to use new line mode for parsing serial communication"})
    delimiter : str = field(default=";", metadata={"description": "delimiter to use in new line mode"})
    
    def __post_init__(self):
        super().__post_init__()
        self.serial : serial.Serial = None
    
    def connect(self) -> bool:
        self.serial = serial.Serial(
            port=self.host,
            baudrate=self.baud_rate,
            timeout=self.timeout
        )
        if self.connect_bytes is not None:
            self._send(self.connect_bytes)
        return True
    
    def disconnect(self) -> bool:
        if self.disconnect_bytes is not None:
            self._send(self.disconnect_bytes)
        self.serial.close()
        return True        
        
    def _send(self, data: bytes):
        if self.send_bytes is not None:
            self.serial.write(self.send_bytes)
        self.serial.write(data)
    
    def _receive(self, n: int) -> bytes:
        if self.before_receive_bytes is not None:
            self.serial.write(self.before_receive_bytes)
        bs : bytes = None
        if self.new_line_mode:           
            if n > 0:
                ba = bytearray()
                for _ in range(n):
                    line = self.serial.readline().decode('utf-8').strip()
                    tu = zip(line.split(self.delimiter))
                    tu_forced = ByteStreamAdapter.force_schema(self.read_byte_schema, tu)
                    ba.extend(self._encode(self.read_byte_schema, tu_forced))
                bs = bytes(ba)
            else:
                line = self.serial.readline().decode('utf-8').strip()                
                tu = zip(line.split(self.delimiter))
                tu_forced = ByteStreamAdapter.force_schema(self.read_byte_schema, tu)
                bs = self._encode(self.read_byte_schema, tu_forced)
        else:
            bs = self.serial.read(n)
        if self.after_receive_bytes is not None:
            self.serial.write(self.after_receive_bytes)
        return bs
    