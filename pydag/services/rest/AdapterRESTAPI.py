from typing import Any, Dict, List, Union
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from pydag.agents.AgentConfig import AgentConfig

from ...adapters.Adapter import Adapter
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils

ROOT_URL : str = "/api/v1/adapters"
 
class AdapterDefinition(BaseModel):
    definition : Dict[str, Any] = Field(default=None, title="adapter config")
        
class AdapterRESTAPI:
    """
    REST API for `Adapter`s using FastAPI.
    Provides endpoints to interact with the adapter instances.
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Adapter.cname()],)
        
        @router.get("/")
        def adapters() -> list[str]:
            """
            Returns a list of all available adapter IDs.
            """
            return list(agent.adapter_store.keys())
        
        @router.get("/available")
        def available_adapters() -> list[str]:
            """ returns a list of adapter package names, that can be created            
            """
            return ClassUtils.get_subclasses(Adapter)                        
        
        @router.get("/config")
        def adapter_config() -> list:
            """
            Returns a list of all adapter configurations.
            """
            li = list()
            for buffer in agent.buffer_store.values():
                d = buffer.config_options()
                li.append(d)
            return li
                
        @router.get("/{id}")
        def adapter(id : str = Path(..., description="unique ID of the adapter")) -> dict:
            adapter : Adapter = agent.get_adapter(id)
            if adapter is None:
                return {"error": "adapter not found"}
            return adapter.config_options()
                      
        @router.post("/")
        def add_adapter(adapter_def : AdapterDefinition) -> str:
            type = adapter_def.definition[AgentConfig.TYPE]
            if not type is None:
                adapter : Adapter = ClassUtils.create_instance(type)
                ClassUtils.set_properties(adapter, adapter_def.definition)            
                agent.add_adapter(adapter)
                return adapter.id
            else:                
                return {"error" : "No " + Adapter.cname() + " with type=" + type + " could be created"}
               
        return router
   