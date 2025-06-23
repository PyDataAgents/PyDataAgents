from dataclasses import dataclass, field
import threading
import websocket

from ...adapters.AdapterException import AdapterException
from ...buffers.Buffer import Buffer
from ..SubscribeAdapter import SubscribeAdapter
from ..WriteAdapter import WriteAdapter


@dataclass
class WebSocketAdapter(WriteAdapter, SubscribeAdapter):
    """`Adapter` for subscribing and writing data from/to WebSocket endpoints.
    """
    
    url : str = field(default=None, metadata={"description":"socket url, e.g. wss://localhost:10001"})
    
    def __init__(self):
        self.socket : websocket.WebSocketApp = None
        self.thread : threading.Thread = None
        
    def __run_socket(self):
        self.socket.run_forever()
    
    def connect(self) -> bool:
        def on_message(ws, message):
            print("📨 Message received:", message)

        def on_error(ws, error):
            print("❌ Error:", error)

        def on_close(ws, close_status_code, close_msg):
            print("🔌 WebSocket closed")

        def on_open(ws):
            print("✅ Connection opened")
        
        self.socket = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        self.thread = threading.Thread(target=self.__run_socket, daemon=True)
        self.thread.start()
        
    def disconnect(self) -> bool:
        self.socket = None
        return True
    
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str] = None, n : int = 0, persistent : bool = True):
        for buffer in buffers.values():
            i = buffer.id
            data = buffer.data(n, persistent)
            d = dict()
            d["id"] = i
            d["data"] = data
            self.socket.send(d)
            
    def subscribe(self, buffers : dict[str, Buffer], addresses : list[str] = None, sampling_period : int = 0, n : int = 0):        
        
        def on_message(ws, message):
            #print("📨 Message received:", message)
            if "id" in message and "data" in message:
                data = message.data
                i = message.id
                if i in buffers:
                    buffers[i].push(data)
                else:
                    raise AdapterException("No " + Buffer.cname() + " with id=" + i + " was found")
            else:
                self.LOGGER.debug("Socket message does not conform with schema {id: <BUFFER_ID>, data: [...]}: " + message)
        
        self.socket.on_message = on_message        
    
