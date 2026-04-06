import threading
from dataclasses import dataclass, field
from typing import Optional
import uvicorn
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles

from ..Service import Service
from ..ServiceException import ServiceException


def create_asgi(root: str, port : int):
    app = Starlette()
    app.mount("/", StaticFiles(directory=root, html=True), name=f"{WebService.__name__}-{port}")
    return app

@dataclass
class WebService(Service):
    root : str = field(default=".")
    host : str = field(default="0.0.0.0")
    port : int = field(default=8080)

    def __post_init__(self):
        super().__post_init__()
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

    def _on_start(self):
        """Start the Uvicorn server in a background thread"""
        if self._server is not None:
            raise ServiceException("WebService already started")

        app = create_asgi(self.root, self.port)
        config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="info")
        self._server = uvicorn.Server(config)

        # Run server in a background thread (non-blocking)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()

    def _on_stop(self):
        """Stop the Uvicorn server"""
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        self._server = None