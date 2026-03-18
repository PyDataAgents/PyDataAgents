from dataclasses import dataclass, field
import threading
from loguru import logger
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from ...agents.Agent import Agent
from ...agents.AgentElement import runtime_handle_field
from ..Service import Service
from .BufferRESTAPI import BufferRESTAPI
from .AgentRESTAPI import AgentRESTAPI
from .AdapterRESTAPI import AdapterRESTAPI
from .ServiceRESTAPI import ServiceRESTAPI
from .NodeRESTAPI import NodeRESTAPI


@dataclass
class RestService(Service):
    """Service for creating a REST API for DataGrabber using FastAPI
    """
    
    port : int = field(default=8001, metadata={"description": "port of the REST API endpoint"})
    _app : FastAPI = runtime_handle_field(default=None, init=False, repr=False)
    _service_thread : threading.Thread = runtime_handle_field(default=None, init=False, repr=False)
    _server : uvicorn.Server = runtime_handle_field(default=None, init=False, repr=False)
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._app = FastAPI(title=agent.__class__.__name__ + " - " + RestService.cname(), docs_url="/docs")
        self.add_cors()
        self.add_router(AgentRESTAPI.get_api_router(self._agent))
        self.add_router(BufferRESTAPI.get_api_router(self._agent))
        self.add_router(AdapterRESTAPI.get_api_router(self._agent))
        self.add_router(ServiceRESTAPI.get_api_router(self._agent))
        self.add_router(NodeRESTAPI.get_api_router(self._agent))
    
    def add_cors(self):
        """Add CORS middleware to the FastAPI app.
        This allows cross-origin requests to the REST API.
        """
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=False,
            allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
            allow_headers=["*"],  # Allows all headers
        )
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._app = None

    def rebuild_runtime_handles(self, agent=None):
        if self._app is None and self._agent is not None:
            self._on_install(self._agent)
        
    def add_router(self, router : APIRouter):
        self._app.include_router(router)
    
    def _on_start(self):
        if self._server is not None and not getattr(self._server, "should_exit", False):
            return
        config = uvicorn.Config(self._app, host="0.0.0.0", port=self.port, reload=False, workers=1, log_level="warning")
        self._server = uvicorn.Server(config)
        self._service_thread = threading.Thread(target=self.__run_uvicorn, daemon=True)
        self._service_thread.start()

    def __run_uvicorn(self):
        if self._server is not None:
            self._server.run()

    def _on_stop(self):
        if self._server is not None:
            self._server.should_exit = True
        if self._service_thread is not None and self._service_thread.is_alive():
            self._service_thread.join(timeout=2.0)
        self._service_thread = None
        self._server = None
        logger.debug("FastAPI server stopped")
