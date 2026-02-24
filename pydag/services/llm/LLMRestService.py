from __future__ import annotations
from dataclasses import dataclass


from ...services.rest.RestService import RestService
from ...agents.Agent import Agent
from .LLMRestAPI import LLMRestAPI


@dataclass
class LLMRestService(RestService):
    """`Service` for creating a REST API for accessing LLM Models
    """         
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._app.include_router(LLMRestAPI.get_api_router(agent))