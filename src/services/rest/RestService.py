from fastapi import FastAPI
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.services.Service import Service
from PyDataGrabber.src.services.rest.GrabberRestAPI import get_grabber_api_router


class RestService(Service):
    """Service for creating a REST API for DataGrabber using FastAPI
    """
    
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