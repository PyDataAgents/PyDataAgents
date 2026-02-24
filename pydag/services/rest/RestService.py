from dataclasses import dataclass, field
import multiprocessing
import threading
from loguru import logger
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from ...agents.Agent import Agent
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
            
    def __post_init__(self):
        super().__post_init__()
        self._app : FastAPI = None
        self._service_thread : threading.Thread = None
        
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
        
    def add_router(self, router : APIRouter):
        self._app.include_router(router)
    
    def _on_start(self):
        multiprocessing.freeze_support()  # For Windows support
        # Start server in a background thread
        self._service_thread = threading.Thread(target=self.__run_uvicorn, daemon=True)
        self._service_thread.start()

    def __run_uvicorn(self):
        uvicorn.run(self._app, host="0.0.0.0", port=self.port, reload=False, workers=1)

    def _on_stop(self):
        #process = subprocess.Popen(
        #    ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", self.port],
        #    stdout=subprocess.PIPE,
        #    stderr=subprocess.PIPE
        #)
        #process.terminate()
        #self.service_thread.join()
        logger.warning("FastAPI Server (uvicorn) shutsdown with application only")
        return
