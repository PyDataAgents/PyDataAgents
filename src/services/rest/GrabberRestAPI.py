from fastapi import APIRouter
from PyDataGrabber.src.grabbers.Grabber import Grabber

def get_grabber_api_router(grabber : Grabber) -> APIRouter:
    router = APIRouter()
    
    @router.get("/")
    def root():
        return {"message": "Welcome to FastAPI for DataGrabber"}
    
    @router.get("/grabber")
    def get_grabber():
        return {"Grabber ID": grabber.id}
    
    return router