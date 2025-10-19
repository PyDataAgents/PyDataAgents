from typing import Any, Dict, List, Union
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from ...services.statemachine.StatemachineService import StatemachineService
from ...agents.AgentConfig import AgentConfig
from ...services.Service import Service
from ...adapters.Adapter import Adapter
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils
from ...nodes.Node import Node

ROOT_URL : str = "/api/v1/nodes"
 
class NodeDefinition(BaseModel):
    statemachine_id : str = Field(default=None, title="unique id of statemachine service to add the new node to")
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
            # TODO
            #node : Node = agent.get_node(id)
            #if node is None:
            #    return {"error": "service not found"}
            return node.config_options()
                      
        @router.post("/")
        def add_node(node_def : NodeDefinition) -> str:
            statemachine_id = node_def.statemachine_id
            type = node_def.definition[AgentConfig.TYPE]
            # TODO check for statemachine_id
            if not type is None:
                node : Node = ClassUtils.create_instance(type)
                ClassUtils.set_properties(node, node_def.definition)            
                # TODO
                #agent.add_service(node)
                return node.id
            else:                
                return {"error" : "No " + Node.cname() + " with type=" + type + " could be created"}
               
        return router
   