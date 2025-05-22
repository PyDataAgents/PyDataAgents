from dataclasses import dataclass, field
from fastapi import FastAPI
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.services.Service import Service
from PyDataGrabber.src.services.rest.GrabberRESTAPI import get_grabber_api_router


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
        self.app.include_router(get_grabber_api_router(self.grabber))
    
    def start(self):
        pass

    def stop(self):
        pass