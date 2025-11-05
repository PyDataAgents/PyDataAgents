from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field

from ...mappings.ThreadType import ThreadType
from ...mappings.Mapping import Mapping
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils

ROOT_URL : str = "/api/v1/mappings"
 
class MappingDefinition(BaseModel):
    type: str = Field(default=None, title="package name of the mapping")
    id : str = Field(default=None, title="unique id")
    buffer_ids : list[str] = Field(default=None, title="list of buffer ids to map from")
    adapter_id : str = Field(default=None, title="id of the Adapter used for this Mapping")
    addresses : list[str] = Field(default_factory=list, title="list of addresses to read/subscribe from or write/publish to")
    thread_type : str = Field(default=ThreadType.MILLI_SECOND.value, title="type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ...")
    mapping_type : str = Field(default=None, title="type of mapping, e.g. READ, WRITE, SUB or PUB")
    n : int = Field(default=1, title="number of samples to insert or remove from buffers")
    sampling_period : int = Field(default=100, title="sampling period to apply in this Mapping")
    persistent : bool = Field(default=True, title="specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink")
    auto_start : bool = Field(default=True, title="specifies whether to start the mapping with agent start")
        
class MappingRESTAPI:
    """ REST API for `Mapping`s using FastAPI.
    Provides endpoints to interact with the mapping instances.
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Mapping.cname()],)
        
        @router.get("/")
        def mappings() -> list[str]:
            """
            Returns a list of all available mapping IDs.
            """
            return list(agent.mapping_store.keys())
        
        @router.get("/available")
        def available_mappings() -> list[str]:
            """ returns a list of mapping package names, that can be created            
            """
            return ClassUtils.get_subclasses(Mapping)                        
        
        @router.get("/config")
        def mapping_type(type : str = Query(..., description="specifies the fully qualified name of the mapping type")) -> dict:
            """
            Returns the specifieds buffer default configuration.
            """
            mapping = ClassUtils.create_instance(type)
            if mapping is None:
                return {}
            elif isinstance(mapping, Mapping):
                return mapping.config_options(with_descriptions=True)
            else:
                return {}
        
        @router.get("/configs")
        def mapping_configs() -> list:
            """
            Returns a list of all mapping configurations.
            """
            li = list()
            for mapping_thread in agent.mapping_store.values():
                d = mapping_thread.mapping.config_options()
                li.append(d)
            return li
        
        @router.get("/usage")
        def mapping_usage(type : str = Query(..., description="type of the mapping (fully qualified package name)")) -> str:
            """
            Returns the usage information for specified `Mapping` type contained in the doc string of the class.
            """
            mapping = ClassUtils.create_instance(type)
            if mapping is None:
                return None
            elif isinstance(mapping, Mapping):
                return mapping.__doc__.strip()
            else:
                return None
                
        @router.get("/{id}")
        def mapping(id : str = Path(..., description="unique ID of the mapping")) -> dict:
            mapping : Mapping = agent.get_mapping(id)
            if mapping is None:
                return {"error": "mapping not found"}
            return mapping.config_options()
                      
        @router.post("/")
        def add_mapping(mapping_def : MappingDefinition) -> str:
            type = mapping_def.type
            if not type is None:
                mapping : Mapping = ClassUtils.create_instance(type)
                ClassUtils.set_properties(mapping, mapping_def.model_dump())            
                agent.add_mapping(mapping)
                return mapping.id
            else:                
                return {"error" : "No " + Mapping.cname() + " with type=" + type + " could be created"}
               
        return router
   