from typing import Any, Dict
from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field


from ..rest.RESTAPIManager import APIRole, RESTAPIManager
from ...agents.AgentConfig import AgentConfig
from ...services.Service import Service
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
        
        @router.get("/configs")
        def service_configs() -> list:
            """
            Returns a list of all service configurations.
            """
            li = list()
            for service in agent.service_store.values():
                d = service.config_options()
                li.append(d)
            return li
        
        @router.get("/usage")
        def service_usage(type : str = Query(..., description="type of the service (fully qualified package name)")) -> str:
            """
            Returns the usage information for specified `Service` type contained in the doc string of the class.
            """
            service = ClassUtils.create_instance(type)
            if service is None:
                return None
            elif isinstance(service, Service):
                return service.__doc__.strip()
            else:
                return None
                
        @router.get("/{id}")
        def service(id : str = Path(..., description="unique ID of the service")) -> dict:
            service : Service = agent.get_service(id)
            if service is None:
                return {"error": "service not found"}
            return service.config_options()
                      
        @router.post("/", dependencies=[Depends(RESTAPIManager.require_min_role(APIRole.WRITE))])
        def add_service(service_def : ServiceDefinition) -> str:
            type = service_def.definition[AgentConfig.TYPE]
            if not type is None:
                service : Service = ClassUtils.create_instance(type)
                ClassUtils.set_properties(service, service_def.definition)            
                agent.add_service(service)
                return service.id
            else:                
                return {"error" : "No " + Service.cname() + " with type=" + type + " could be created"}
        
        @router.get("/{id}/start")
        def start_service(id : str = Path(..., description="unique ID of the service")) -> dict:
            service : Service = agent.get_service(id)
            if service is None:
                return {"error": "service not found"}
            else:
                service.start()
                return {"success": True}
        
        @router.get("/{id}/stop")
        def stop_service(id : str = Path(..., description="unique ID of the service")) -> dict:
            service : Service = agent.get_service(id)
            if service is None:
                return {"error": "service not found"}
            else:
                service.stop()
                return {"success": True}
                   
        return router
   