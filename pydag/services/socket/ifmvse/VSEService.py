from dataclasses import dataclass, field
import enum
import socket
import struct
import threading
from loguru import logger

from ...ServiceException import ServiceException
from ...SubscribeService import SubscribeService
from ....agents.AgentStates import AgentElementState
from ....buffers.Buffer import Buffer

MSG_ID_BYTES : int = 2
MSG_ID_FORMAT : str = "<h"

class Message():    
    def __init__(self, id : int = 0,  n : int = 0, sch : str = None):
        self.id = id
        self.n = n
        self.sch = sch
    
class Messages(Message, enum.Enum):    
    """
    collection of messages consisting og id, n/um of bytes) and sch(ema)
    """
    
    MSG_ACK = Message(0, 12, "<hhhhhh")
    """ 
    +-------+----------+----------+----------------------+------------------------------------+
    | index | datatype | value    | name                 | flag                               |
    +-------+----------+----------+----------------------+------------------------------------+
    | +0    | s16      | 0        | msgId                | MSG_ACK                            |
    | +2    | s16      | 0        | -                    |                                    |
    | +4    | s16      | 0..      | ackMsgId             | msgId of confirmed message         |
    | +6    | s16      |          | ackId                | additional Id of confirmed message |
    | +8    | s16      | 0, <0    | status               | status of confirmed message        |
    | +10   | s16      |          | reserved             |                                    |
    +-------+----------+----------+----------------------+------------------------------------+
    """
        
    MSG_SET_MODE = Message(34, 8, "<hhHH")
    """
    +-------+----------+-------+------------+------------------------+
    | index | datatype | value | name       | flag                   |
    +-------+----------+-------+------------+------------------------+
    | +0    | s16      | 34    | msgId      | MSG_SET_MODE           |
    | +2    | s16      | 0     | -          |                        |
    | +4    | u16      | 0     | systemMode | systemmode 0, 1, 2, 3 |
    | +6    | u16      | 0     | reserved   |                        |
    +-------+----------+-------+------------+------------------------+
    """   
    
    MSG_DO_MEASURE = Message(50, 24, "<hhHHIfIHH")
    """
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
    
    MSG_MEASURE_STREAM = Message(203, 1412, "<hhfHH700h")
    """
    +-------+-----------+------------+----------------------+------------------------+
    | index | datatype  | value      | name                 | flag                   |
    +-------+-----------+------------+----------------------+------------------------+
    | +0    | s16       | 203        | msgId                | MSG_MEASURE_STREAM     |
    | +2    | s16       | 0          | -                    |                        |
    | +4    | float     |            | scale                | scale factor           |
    | +8    | u16       | 700 (typ.) | size                 | number of samples      |
    | +10   | u16       | 700 (typ.) | size2                | like size              |
    | +12   | s16[size] |            | samples[size]        | input data             |
    +-------+-----------+------------+----------------------+------------------------+
    """

@dataclass
class VSEService(SubscribeService):
   
    host : str = field(default="192.168.0.1", metadata={"description": "ip address or host name of the vse host device"})
    port : int = field(default=3321, metadata={"description": "port of the vse host device"})
    sensor : int = field(default=1, metadata={"description": "sensor number to measure"})
    sample_rate : int = field(default=10000, metadata={"description": "sample rate in Hz from 1.000 Hz to 100.000 Hz"})
    timeout : int = field(default=3, metadata={"description": "socket timeout, any blocking operation (connect, recv, send, accept) will wait max 'timeout' seconds"})
        
    def __post_init__(self):
        super().__post_init__()
        self._socket : socket.socket = None
        self._mode : int = None
        self._thread : threading.Thread = None
        self._is_measuring : bool = False
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        # Create a TCP/IP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self.timeout)
        # Connect to the server
        try:
            self._socket.connect((self.host, self.port))
        except TimeoutError as e:
            raise ServiceException(f"Could not connect to socket in {self.__class__.__name__}") from e
       
    def _on_uninstall(self, agent = None):
        super()._on_uninstall(agent)
        if self._socket is not None:
            try:
                self._socket.close()
                self._socket = None
                self._thread = None
            except Exception as e:
                raise ServiceException(f"could not disconnect from socket in {self.__class__.__name__}") from e
             
    def subscribe(self):        
        buffer : Buffer = next(iter(self.get_buffers().values()))
        # start the message processing task
        if not self._is_measuring:
            self._thread = threading.Thread(target=self._process_incoming_messages, args = [buffer], daemon=True, name=f"{self.__class__.__name__}-{self.id}-MessageThread")
            self._is_measuring = True
            self._thread.start()
            try:
                self._set_mode(3)  # set to measurement mode
                self._start_measure(sensor=self.sensor, sample_rate=self.sample_rate)  # start measurement msg
            except (ConnectionAbortedError, ConnectionResetError) as e:
                raise ServiceException("Connection to VSE device was interrupted") from e

        
    def unsubscribe(self):
        self._is_measuring = False
        if self._thread:
            self._thread.join()
            self._thread = None
            
    def _set_mode(self, mode : int):
        """
        changes the system mode of the VSE device
        
        modes:
        0 = Selftest
        1 = Supervise
        2 = Setup
        3 = Measure
        
        """
        bm = bytearray(Messages.MSG_SET_MODE.value.n)
        bm[0:2] = struct.pack(MSG_ID_FORMAT, Messages.MSG_SET_MODE.value.id)
        bm[4:6] = struct.pack("<H", mode)
        if self._socket is None:
            raise RuntimeError("Socket not connected")
        self._socket.sendall(bm)
      
    def _start_measure(self, sensor : int, sample_rate : int):
        """
        starts the measurement for a given sensor (1-4) at a given sample rate ( 1000 Hz to 100.000 Hz)
        """
        bm = bytearray(Messages.MSG_DO_MEASURE.value.n)
        bm[0:2] = struct.pack(MSG_ID_FORMAT, Messages.MSG_DO_MEASURE.value.id)  # MSG_DO_MEASURE
        bm[2:4] = struct.pack("<h", sensor - 1)            # sensorId, which is zero based
        bm[4:6] = struct.pack("<H", 4)                  # NOT SURE WHY 4 has to be passed here, should be 2 according to manual
        d_sr = int(100000 / sample_rate)
        bm[20:22] = struct.pack("<H", d_sr)               # divideSampleRateFreq
        if self._socket is None:
            raise RuntimeError("Socket not connected")
        self._socket.sendall(bm)
        
    def _read_msg(self, msg_id : int, msg_byte_num : int) -> bytes:
        b_ar = bytearray(MSG_ID_BYTES)
        b_ar[0:MSG_ID_BYTES] = struct.pack(MSG_ID_FORMAT, msg_id)
        bs = self._socket.recv(msg_byte_num - MSG_ID_BYTES)
        b_ar.extend(bs)
        return bytes(b_ar)

    def _process_incoming_messages(self, buffer : Buffer):
        try: 
            while self._is_measuring:
                id_bytes = self._socket.recv(MSG_ID_BYTES)                        
                msg_id = list(struct.unpack(MSG_ID_FORMAT, id_bytes))[0]
                #print(msg_id)
                match(msg_id):
                    case Messages.MSG_ACK.value.id:
                        bs = self._read_msg(msg_id, Messages.MSG_ACK.value.n)
                        d = struct.unpack(Messages.MSG_ACK.value.sch, bs)
                    case Messages.MSG_SET_MODE.value.id:
                        bs = self._read_msg(msg_id, Messages.MSG_SET_MODE.value.n)
                        d = struct.unpack(Messages.MSG_SET_MODE.value.sch, bs)
                    case Messages.MSG_DO_MEASURE.value.id:
                        bs = self._read_msg(msg_id, Messages.MSG_DO_MEASURE.value.n)
                        d = struct.unpack(Messages.MSG_DO_MEASURE.value.sch, bs)
                    case Messages.MSG_MEASURE_STREAM.value.id:
                        bs = self._read_msg(msg_id, Messages.MSG_MEASURE_STREAM.value.n)
                        d = struct.unpack(Messages.MSG_MEASURE_STREAM.value.sch, bs)
                        samples = list(d[6:])
                        buffer.push(samples)
                    case _:
                        d = None
                    
                #print(d)
        except (ConnectionAbortedError, ConnectionResetError, Exception) as e:
            self._is_measuring = False
            self._state = AgentElementState.ERROR
            logger.error(e)
                              