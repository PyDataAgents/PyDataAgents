from fastapi import APIRouter
from PyDataGrabber.src.grabbers.Grabber import Grabber

ROOT_URL : str = "/grabber/api/v1"

class GrabberRESTAPI:
    """
    REST API for DataGrabber using FastAPI.
    Provides endpoints to interact with the Grabber instance.
    """
   
    @staticmethod
    def get_api_router(grabber : Grabber) -> APIRouter:
        
        router = APIRouter()
        
        @router.get(ROOT_URL + "/hello")
        def hello():
            return {"message": "Welcome to FastAPI for DataGrabber"}
        
        @router.get(ROOT_URL)
        def get_grabber():
            return {"Grabber ID": grabber.id}
        
        return router