from typing import Any, Dict, List, Union
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from ...agents.AgentConfig import AgentConfig
from ...services.Service import Service
from ...adapters.Adapter import Adapter
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils

ROOT_URL : str = "/api/v1/services"
 
class ServiceDefinition(BaseModel):
    definition : Dict[str, Any] = Field(default=None, title="service config")
        
class ServiceRESTAPI:
    """
    REST API for `Services`s using FastAPI.
    Provides endpoints to interact with the service instances.
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Service.cname()],)
        
        @router.get("/")
        def services() -> list[str]:
            """
            Returns a list of all available service IDs.
            """
            return list(agent.service_store.keys())
        
        @router.get("/available")
        def available_services() -> list[str]:
            """ returns a list of service package names, that can be created            
            """
            return ClassUtils.get_subclasses(Service)                        
        
        @router.get("/config")
        def service_config() -> list:
            """
            Returns a list of all service configurations.
            """
            li = list()
            for service in agent.service_store.values():
                d = service.config_options()
                li.append(d)
            return li
                
        @router.get("/{id}")
        def service(id : str = Path(..., description="unique ID of the service")) -> dict:
            service : Service = agent.get_service(id)
            if service is None:
                return {"error": "service not found"}
            return service.config_options()
                      
        @router.post("/")
        def add_service(service_def : ServiceDefinition) -> str:
            type = service_def.definition[AgentConfig.TYPE]
            if not type is None:
                service : Service = ClassUtils.create_instance(type)
                ClassUtils.set_properties(service, service_def.definition)            
                agent.add_service(service)
                return service.id
            else:                
                return {"error" : "No " + Service.cname() + " with type=" + type + " could be created"}
               
        return router
   