from __future__ import annotations
from dataclasses import dataclass
from fastapi import FastAPI

from ...services.Service import Service
from ...services.rest.RestService import RestService
from ...agents.Agent import Agent
from .LLMRestAPI import LLMRestAPI


@dataclass
class LLMRestService(RestService):
    """`Service` for creating a REST API for accessing LLM Models
    """         
        
    def install(self, agent : Agent = None):
        super(Service, self).install()
        self.app = FastAPI(title=Agent.cname() + " " + self.cname(), docs_url="/docs")
        self.add_cors()
        self.app.include_router(LLMRestAPI.get_api_router(agent))
        
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        self.app = None