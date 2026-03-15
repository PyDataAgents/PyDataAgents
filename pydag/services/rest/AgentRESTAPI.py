from typing import Union
from fastapi import APIRouter, Body, Path
from pydantic import BaseModel, Field


from ...agents.AgentElement import AgentElement
from ...agents.Agent import Agent
from ...agents.AgentConfig import AgentConfig
from ...agents.RuntimeStorage import CleanupScope

ROOT_URL : str = "/api/v1/agent"

class ElementDefinition(BaseModel):
    prop : str = Field(default=None, title="the property to change")
    value : Union[float | int | bool | str | list | dict]  = Field(default = None, title="new value for the property")
    requires_install : bool = Field(default=True, title="specifies whether an install is required after setting property")


class CleanupDefinition(BaseModel):
    scope: str = Field(default=CleanupScope.REBUILDABLE_OWNER_CACHE.value, title="cleanup scope")
    dry_run: bool = Field(default=False, title="if true only list candidates")
    keep_last_n_checkpoints: int = Field(default=3, title="number of checkpoints to retain for pruning")

class AgentRESTAPI:
    """
    REST API for Data Agent using FastAPI.
    Provides endpoints to interact with the `Agent` instance.
    """

    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Agent.__name__])
        
        @router.get("/")
        def online():
            return True
        
        @router.get("/config")
        def config():
            return agent.config_options()
        
        @router.get("/description")
        def description():
            return agent.description

        @router.get("/status")
        def status():
            return agent.status()

        @router.put("/config/{id}")
        def set_element_property(id : str = Path(..., description="the id of the element to be changed"),
                                 element_definition : ElementDefinition = None) -> dict:
            if element_definition is None:
                return {"success": False, "error": "No element definition provided."}
            element : AgentElement = agent.get_element(id)
            if not element:
                return {"success": False, "error": f"Element with id '{id}' not found."}
            if not hasattr(element, element_definition.prop):
                return {"success": False, "error": f"Property '{element_definition.prop}' not found in element with id '{id}'."}
            setattr(element, element_definition.prop, element_definition.value)
            if element_definition.requires_install:
                element.install(agent)
            return {"success": True, "message": f"Property '{element_definition.prop}' of element with id '{id}' updated successfully to {element_definition.value}."}

        @router.post("/pause")
        def pause():
            agent.pause()
            return {"success": True, "status": agent.status()}

        @router.post("/resume")
        def resume():
            agent.resume()
            return {"success": True, "status": agent.status()}

        @router.post("/checkpoint")
        def checkpoint():
            manifest = agent.checkpoint()
            return {"success": True, "checkpoint": manifest}

        @router.post("/reload")
        def reload_current():
            success = agent.reload_current()
            return {"success": success, "status": agent.status()}

        @router.post("/cleanup")
        def cleanup(cleanup_definition: CleanupDefinition = Body(default=None)):
            if cleanup_definition is None:
                cleanup_definition = CleanupDefinition()
            report = agent.cleanup(
                scope=cleanup_definition.scope,
                dry_run=cleanup_definition.dry_run,
                keep_last_n_checkpoints=cleanup_definition.keep_last_n_checkpoints,
            )
            return {"success": True, "cleanup": report}
                
        return router
