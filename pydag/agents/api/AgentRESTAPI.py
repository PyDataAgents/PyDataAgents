from __future__ import annotations
from typing import TYPE_CHECKING, Union
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field


from .RESTAPIManager import APIRole, RESTAPIManager
from ..AgentElement import AgentElement

if TYPE_CHECKING:
    from ..Agent import Agent


ROOT_URL : str = "/api/v1/agent"

class ElementDefinition(BaseModel):
    prop : str = Field(default=None, title="the property to change")
    value : Union[float | int | bool | str | list | dict]  = Field(default = None, title="new value for the property")
    requires_install : bool = Field(default=True, title="specifies whether an install is required after setting property")

class AgentRESTAPI:
    """
    REST API for Data Agent using FastAPI.
    Provides endpoints to interact with the `Agent` instance.
    """

    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        from ..Agent import Agent 
        router = APIRouter(prefix=ROOT_URL, tags=[Agent.__name__])
        
        @router.get("/")
        def online():
            return True
        
        @router.get("/config", dependencies=[Depends(RESTAPIManager.require_min_role(APIRole.ADMIN))])
        def config():
            return agent.config_options()
        
        @router.get("/description")
        def description():
            return agent.description
        
        @router.put("/config/{id}", dependencies=[Depends(RESTAPIManager.require_min_role(APIRole.ADMIN))])
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
                        
        return router