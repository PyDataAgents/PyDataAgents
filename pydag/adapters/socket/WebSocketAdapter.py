from dataclasses import dataclass, field
import threading
import websocket
import json
from loguru import logger


from ...agents.Agent import Agent
from ...adapters.AdapterException import AdapterException
from ...buffers.Buffer import Buffer
from ..SubscribeAdapter import SubscribeAdapter
from ..WriteAdapter import WriteAdapter


@dataclass
class WebSocketAdapter(WriteAdapter, SubscribeAdapter):
    """`Adapter` for subscribing and writing data from/to WebSocket endpoints.
    """
    
    url : str = field(default=None, metadata={"description":"socket url, e.g. wss://localhost:10001"})
    
    def __post_init__(self):
        super().__post_init__()
        self._socket : websocket.WebSocketApp = None
        self._thread : threading.Thread = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        
    def _run_socket(self):
        if self._socket is not None:
            self._socket.run_forever()
    
    def _on_connect(self) -> bool:
        def on_message(ws, message):
            print("📨 Message received:", message)

        def on_error(ws, error):
            print("❌ Error:", error)

        def on_close(ws, close_status_code, close_msg):
            print("🔌 WebSocket closed")

        def on_open(ws):
            print("✅ Connection opened")
        
        self._socket = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        self._thread = threading.Thread(target=self._run_socket, daemon=True)
        self._thread.start()
        return True
        
    def _on_disconnect(self) -> bool:
        if self._socket is not None:
            try:
                # attempt an orderly close
                self._socket.close()
            except Exception:
                logger.debug("Error while closing websocket")
            self._socket = None
        # thread is daemon; it will exit when socket.run_forever stops
        self._thread = None
        return True
    
    def _on_write(self, buffers : dict[str, Buffer], addresses : list[str] = None, n : int = 0, persistent : bool = True):
        for buffer in buffers.values():
            i = buffer.id
            data = buffer.data(n, persistent)
            d = dict()
            d["id"] = i
            d["data"] = data
            if self._socket is None:
                raise AdapterException("WebSocket is not connected")
            try:
                self._socket.send(json.dumps(d))
            except Exception as e:
                raise AdapterException("Failed to send websocket message") from e
            
    def _on_subscribe(self, buffers : dict[str, Buffer], addresses : list[str] = None, sampling_period : int = 0, n : int = 0, error_callback : callable = None):        
        
        def on_message(ws, message):
            #print("📨 Message received:", message)
            if "id" in message and "data" in message:
                data = message.data
                i = message.id
                if i in buffers:
                    buffers[i].push(data)
                else:
                    if error_callback:
                        error_callback(AdapterException("No " + Buffer.cname() + " with id=" + i + " was found"))
                    raise AdapterException("No " + Buffer.cname() + " with id=" + i + " was found")
            else:
                logger.error("Socket message does not conform with schema {id: <BUFFER_ID>, data: [...]}: " + message)
        
        if self._socket is None:
            raise AdapterException("WebSocket is not connected")
        self._socket.on_message = on_message        
    
