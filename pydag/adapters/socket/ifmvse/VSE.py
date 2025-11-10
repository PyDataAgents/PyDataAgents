import enum
import socket
import struct
import threading

from ....buffers import Buffer

MSG_ID_BYTES : int = 2

class MsgId(int, enum.Enum):
    MSG_ACK = 0
    MSG_SET_MODE = 34
    MSG_DO_MEASURE = 50
    
class MsgBytes(int, enum.Enum):
    MSG_ACK = 12
    MSG_SET_MODE = 8
    MSG_DO_MEASURE = 24

class VSE():
   
    def __init__(self, host : str = "192.168.0.1", port : int = 3321):
        self.socket : socket.socket = None
        self.host : str = host
        self.port : int = port
        self.mode : int = None
        self.thread : threading.Thread = None
        self.buffer : Buffer = None
        self.is_measuring : bool = False
    
    def connect(self) -> bool:
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.socket.connect((self.host, self.port))
        return True
    
    def disconnect(self) -> bool:
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        return True
    
    def start(self, sensor : int = 1, sample_rate : int = 100000):
        """
        starts the VSE device in measurement mode
        """
        # start the message processing task
        self.thread = threading.Thread(target=self._process_incoming_messages)        
        self.is_measuring = True
        self.thread.start()
        self._set_mode(3)  # set to measurement mode
        self._start_measure(sensor=sensor, sample_rate=sample_rate)  # start measurement msg
    
    def stop(self):
        self.is_measuring = False
    
    def set_buffer(self, buffer : Buffer):
        self.buffer = buffer
        
    def _set_mode(self, mode : int):
        """
        changes the system mode of the VSE device
        
        modes:
        0 = Selftest
        1 = Supervise
        2 = Setup
        3 = Measure
        
        +-------+----------+-------+------------+------------------------+
        | index | datatype | value | name       | flag                   |
        +-------+----------+-------+------------+------------------------+
        | +0    | s16      | 34    | msgId      | MSG_SET_MODE           |
        | +2    | s16      | 0     | -          |                        |
        | +4    | u16      | 0     | systemMode | systemmode 0, 1, 2, 3 |
        | +6    | u16      | 0     | reserved   |                        |
        +-------+----------+-------+------------+------------------------+
        
        """
        bm = bytearray(MsgBytes.MSG_SET_MODE.value)
        bm[0:2] = struct.pack("<h", MsgId.MSG_SET_MODE.value)
        bm[4:6] = struct.pack("<H", mode)
        self.socket.sendall(bm)
      
    def _start_measure(self, sensor : int, sample_rate : int):
        """
        starts the measurement for a given sensor (1-4) at a given sample rate ( 1000 Hz to 100.000 Hz)
        
        +-------+----------+----------+----------------------+------------------------+
        | index | datatype | value    | name                 | flag                   |
        +-------+----------+----------+----------------------+------------------------+
        | +0    | s16      | 50       | msgId                | MSG_DO_MEASURE         |
        | +2    | s16      | 0 .. 3   | sensorId             | sensor input (0-index) |
        | +4    | u16      | 0        | type                 | measure type 0, 1, 2   |
        | +6    | u16      | 0        | mode                 | measure mode 0, 1, 6   |
        | +8    | u32      | 0        | n samples            |                        |
        | +12   | float    | 0        | freqStart            |                        |
        | +16   | u32      | 0        | decimate             |                        |
        | +20   | u16      | 1 .. 100 | divideSampleRateFreq |                        |
        | +22   | u16      | 0        | divideSampleRateTime |                        |
        +-------+----------+----------+----------------------+------------------------+
        
        """
        bm = bytearray(MsgBytes.MSG_DO_MEASURE.value)
        bm[0:2] = struct.pack("<h", MsgId.MSG_DO_MEASURE.value)  # MSG_DO_MEASURE
        bm[2:4] = struct.pack("<h", sensor - 1)            # sensorId
        bm[4:6] = struct.pack("<H", 4)                  # NOT SURE WHY 4 has to be passed here, should be 2 according to manual
        d_sr = int(100000 / sample_rate)
        bm[20:22] = struct.pack("<H", d_sr)               # divideSampleRateFreq
        self.socket.sendall(bm)

    def _process_incoming_messages(self):
        #while self.is_measuring:
        #self.socket.
        pass