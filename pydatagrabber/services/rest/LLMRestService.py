from __future__ import annotations
from dataclasses import dataclass, field
from fastapi import FastAPI

from .LLMRestAPI import LLMRestAPI
from ..Service import Service
from .RestService import RestService
from ...grabbers.Grabber import Grabber


@dataclass
class LLMRestService(RestService):
    """Service for creating a REST API for accessing LLM Models
    """
         
    def __init__(self):
        super().__init__()
        
    def install(self, grabber : Grabber = None):
        super(Service, self).install()
        self.app = FastAPI(title="DataGrabber " + self.cname(), docs_url="/docs")
        self.app.include_router(LLMRestAPI.get_api_router(grabber))
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.app = None