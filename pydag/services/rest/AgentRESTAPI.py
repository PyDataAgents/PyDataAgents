from fastapi import APIRouter

from ...agents.Agent import Agent
from ...agents.AgentConfig import AgentConfig

ROOT_URL : str = "/api/v1/agent"

class AgentRESTAPI:
    """
    REST API for Data Agent using FastAPI.
    Provides endpoints to interact with the `Agent` instance.
    """

    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Agent.cname()])
        
        @router.get("/")
        def online():
            return True
        
        @router.get("/config")
        def config():
            return AgentConfig(agent).to_dict()
                
        return router