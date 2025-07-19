from fastapi import APIRouter
from ...grabbers.Grabber import Grabber
from ...grabbers.GrabberConfig import GrabberConfig

ROOT_URL : str = "/api/v1/grabber"

class GrabberRESTAPI:
    """
    REST API for DataGrabber using FastAPI.
    Provides endpoints to interact with the Grabber instance.
    """

    @staticmethod
    def get_api_router(grabber : Grabber) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["Grabber"])
        
        @router.get("/")
        def online():
            return True
        
        @router.get("/config")
        def config():
            return GrabberConfig(grabber).to_dict()
                
        return router