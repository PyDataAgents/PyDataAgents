from dataclasses import dataclass, field
import multiprocessing
import threading
from fastapi import APIRouter, FastAPI
import uvicorn
from ...grabbers.Grabber import Grabber
from ..Service import Service
from .BufferRESTAPI import BufferRESTAPI
from .GrabberRESTAPI import GrabberRESTAPI


@dataclass
class RestService(Service):
    """Service for creating a REST API for DataGrabber using FastAPI
    """
    
    port : int = field(default=8001, metadata={"description": "port of the REST API endpoint"})
            
    def __init__(self):
        super().__init__()
        self.app : FastAPI = None
        self.service_thread : threading.Thread = None
        
    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.app = FastAPI(title="DataGrabber", docs_url="/docs")
        self.app.include_router(GrabberRESTAPI.get_api_router(self.grabber))
        self.app.include_router(BufferRESTAPI.get_api_router(self.grabber))
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.app = None
        
    def add_router(self, router : APIRouter):
        self.app.include_router(router)
    
    def start(self):
        multiprocessing.freeze_support()  # For Windows support
        # Start server in a background thread
        self.service_thread = threading.Thread(target=self.__run_uvicorn, daemon=True)
        self.service_thread.start()

    def __run_uvicorn(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, reload=False, workers=1)

    def stop(self):
        #process = subprocess.Popen(
        #    ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", self.port],
        #    stdout=subprocess.PIPE,
        #    stderr=subprocess.PIPE
        #)
        #process.terminate()
        #self.service_thread.join()
        self.LOGGER.warning("FastAPI Server (uvicorn) shutsdown with application only")
        return
