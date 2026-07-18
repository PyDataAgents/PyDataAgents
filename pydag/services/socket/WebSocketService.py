from dataclasses import dataclass, field
import threading
import websocket
import json
from loguru import logger


from ...agents.AgentStates import AgentElementState
from ..ServiceException import ServiceException
from ..SubscribeService import SubscribeService
from ..WriteService import WriteService
from ...agents.Agent import Agent
from ...buffers.Buffer import Buffer


@dataclass
class WebSocketService(WriteService, SubscribeService):
    """`MappingService` for subscribing and writing data from/to WebSocket endpoints.
    """
    
    url : str = field(default=None, metadata={"description":"socket url, e.g. wss://localhost:10001"})
    
    def __post_init__(self):
        super().__post_init__()
        self._socket : websocket.WebSocketApp = None
        self._thread : threading.Thread = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        
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
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self._socket is not None:
            try:
                # attempt an orderly close
                self._socket.close()
            except Exception:
                logger.debug("Error while closing websocket")
            self._socket = None
        # thread is daemon; it will exit when socket.run_forever stops
        self._thread = None
                    
    def write_to_sink(self):
        for buffer in self.get_buffers().values():
            id = buffer.id
            data = buffer.data(n=self.n, persistent=self.persistent)
            d = dict()
            d["id"] = id
            d["data"] = data
            if self._socket is None:
                raise ServiceException("WebSocket is not connected")
            try:
                self._socket.send(json.dumps(d))
            except Exception as e:
                raise ServiceException("Failed to send websocket message") from e
            
    def subscribe(self):
        
        def on_message(ws, message):
            #print("📨 Message received:", message)
            if "id" in message and "data" in message:
                data = message.data
                id = message.id
                if id in self.get_buffers():
                    self.get_buffers()[id].push(data)
                else:
                    logger.error(f"No {Buffer.__class__.__name__} with id={id} was found")
                    self._state = AgentElementState.ERROR
            else:
                logger.error("Socket message does not conform with schema {id: <BUFFER_ID>, data: [...]}: " + message)
                self._state = AgentElementState.ERROR
        
        if self._socket is None:
            raise ServiceException("WebSocket is not connected")
        self._socket.on_message = on_message
        
        self._thread = threading.Thread(target=self._run_socket, daemon=True)
        self._thread.start()
        
    def _run_socket(self):
        if self._socket is not None:
            self._socket.run_forever()
    
