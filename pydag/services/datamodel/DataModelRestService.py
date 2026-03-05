from __future__ import annotations
from dataclasses import dataclass


from ...services.rest.RestService import RestService
from ...agents.Agent import Agent
from .DataModelRestAPI import DataModelRestAPI


@dataclass
class DataModelRestService(RestService):
    """`Service` for creating a REST API for accessing DataModels
    """         
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self.add_router(DataModelRestAPI.get_api_router(self._agent))