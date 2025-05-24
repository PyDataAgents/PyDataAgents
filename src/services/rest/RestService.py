from dataclasses import dataclass, field
from fastapi import APIRouter, FastAPI
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.services.Service import Service
from PyDataGrabber.src.services.rest.GrabberRESTAPI import GrabberRESTAPI


@dataclass
class RestService(Service):
    """Service for creating a REST API for DataGrabber using FastAPI
    """
    
    port : int = field(default=8000, metadata={"description": "port of the REST API endpoint"})
        
    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        
    def set_grabber(self, grabber : Grabber):
        self.grabber = grabber
        self.app.include_router(GrabberRESTAPI.get_api_router(self.grabber))
    
    def add_router(self, router : APIRouter):
        self.app.include_router(router)
    
    def start(self):
        pass

    def stop(self):
        pass