from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field


from ...services.Service import Service
from ...nodes.TriggerAction import TriggerAction
from ...services.statemachine.StatemachineService import StatemachineService
from ..AgentConfig import AgentConfig
from ...utils.ClassUtils import ClassUtils
from ...nodes.Node import Node
from .RESTAPIManager import APIRole, RESTAPIManager

if TYPE_CHECKING:
    from ..Agent import Agent

ROOT_URL : str = "/api/v1/nodes"

class NodeDefinition(BaseModel):
    definition : Dict[str, Any] = Field(default=None, title="node config")
        
class NodeRESTAPI:
    """
    REST API for `Node`s using FastAPI.
    Provides endpoints to interact with the node instances within `Statemachine` `Service`s.
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Node.cname()],)
          
        
        @router.get("/")
        def nodes() -> list[str]:
            """
            Returns a list of all available node IDs.
            """
            # TODO
            return list(agent.service_store.keys())
        
        @router.get("/statemachines")
        def statemachines() -> list[str]:
            """
            Returns a list of all available node IDs.
            """
            return list(agent.get_services(StatemachineService))
          
        @router.get("/available")
        def available_nodes() -> list[str]:
            """ returns a list of node package names, that can be created            
            """
            return ClassUtils.get_subclasses(Node)                        
        
        @router.get("/config")
        def node_config() -> list:
            """
            Returns a list of all node configurations.
            """
            li = list()
            # TODO
            #for node in agent.service_store.values():
            #    d = service.config_options()
            #   li.append(d)
            return li
                
        @router.get("/{id}")
        def node(id : str = Path(..., description="unique ID of the node")) -> dict:
            node : Node = agent.get_node(id)
            if node:
                return node.config_options()
            else:
                return {}
                      
        @router.post("/{service_id}/add", dependencies=[Depends(RESTAPIManager.require_min_role(APIRole.WRITE))])
        def add_node(node_def : NodeDefinition, service_id: str = Path(..., description="")) -> Any:
            """ add a new node based on `node_def` for specified `Service` with `service_id`

            Args:
                node_def (NodeDefinition): dictionary with node configuration properties
                service_id (str, optional): unique id of the statemachine service to add the node to

            Returns:
                str: returns the node id of the new node
            """
            # check if service exists
            service = agent.get_service(service_id)
            if service:
                if isinstance(service, StatemachineService):
                    type = node_def.definition[AgentConfig.TYPE]
                    available_nodes = ClassUtils.get_subclasses(Node)
                    if type in available_nodes:
                        if type:
                            node : Node = ClassUtils.create_instance(type)
                            ClassUtils.set_properties(node, node_def.definition)            
                            service.add_node(node)
                            return node.id
                        else:                
                            return {"error" : "No type was defined for " + Node.cname() + " creation"}
                    else:
                        return {"error": Node.cname() + " of type=" + type + " is not available in this Agent"}
                else:
                    return {"error" : "The specified " + Service.cname() + " is not of type " + StatemachineService.cname()}  
            else:
                return {"error" : "No " + Service.cname() + " with id=" + service_id + " exists in this Agent"}            
            
        
        @router.get("/{id}/trigger")
        def trigger_node(id: str = Path(..., description="unique ID of the node to trigger")) -> dict:
            node : Node = agent.get_node(id)
            if node:
                if isinstance(node, TriggerAction):
                    node.trigger()
                    return {"status": "triggered"}
                else:
                    return {"error" : Node.cname() + " with id=" + id + " is not a " + TriggerAction.cname()}
            else:
                return {"error" : "No " + Node.cname() + " with id=" + id + " was found"}
            
        return router
   