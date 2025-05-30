from dataclasses import dataclass, field
from fastapi import APIRouter, FastAPI
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.services.Service import Service
from PyDataGrabber.services.rest.BufferRESTAPI import BufferRESTAPI
from PyDataGrabber.services.rest.GrabberRESTAPI import GrabberRESTAPI


@dataclass
class RestService(Service):
    """Service for creating a REST API for DataGrabber using FastAPI
    """
    
    port : int = field(default=8000, metadata={"description": "port of the REST API endpoint"})
        
    def __init__(self):
        super().__init__()
        self.app = FastAPI(title="DataGrabber", docs_url="/docs")
        
    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.grabber = grabber
        self.app.include_router(GrabberRESTAPI.get_api_router(self.grabber))
        self.app.include_router(BufferRESTAPI.get_api_router(self.grabber))
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.app = None
        
    def add_router(self, router : APIRouter):
        self.app.include_router(router)
    
    def start(self):
        pass

    def stop(self):
        pass