from typing import Any, Dict, List, Union
from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field
from ...buffers.Buffer import Buffer
from ...buffers.DataType import DataType
from ...buffers.ListBuffer import ListBuffer
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils

ROOT_URL : str = "/api/v1/buffers"
 
class BufferDefinition(BaseModel):
    type : str = Field(default=ListBuffer.__module__, title="type of the buffer to create")
    id : str = Field(default=ListBuffer().unique_id(), title="unique identifer throughout agent application")
    capacity : int = Field(default=1, title="number of elements that can be stored in buffer before being discarded in FiFo fashion")
    data_type : str = Field(default=DataType.FLOAT.value, title="datatype to expect from buffer elements, can be DataType enum or list of enums")
    initial_values : Any = Field(default=None, title="initial values in buffer")
    unit : Any = Field(default=None, title="unit of element values in this buffer, can be string or list of strings")
    description : str = Field(default=None, title="buffer description")

class BufferData(BaseModel):
    data: Union[Any, List[Any], Dict[str, Any]]
        
class BufferRESTAPI:
    """
    REST API for Buffers using FastAPI.
    Provides endpoints to interact with the buffer instances.
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[Buffer.cname()],)
        
        @router.get("/")
        def buffers() -> list[str]:
            """
            Returns a list of all available buffer IDs.
            """
            return list(agent.buffer_store.keys())
        
        @router.get("/config")
        def buffer_config(with_sizes : bool = Query(False, description="specifies whether to return the current size on top of configurations")) -> list:
            """
            Returns a list of all buffer configurations.
            """
            li = list()
            for buffer in agent.buffer_store.values():
                d = buffer.config_options()
                if with_sizes:
                    d["size"] = buffer.size()
                li.append(d)
            return li
                
        @router.get("/{id}")
        def buffer(id : str = Path(..., description="unique ID of the buffer")) -> dict:
            buffer : Buffer = agent.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            return buffer.config_options()
        
        @router.get("/{id}/size")
        def buffer_size(id : str = Path(..., description="unique ID of the buffer")) -> int:
            """
            Returns the size of the specified buffer.
            """
            buffer : Buffer = agent.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            return buffer.size()
        
        @router.get("/{id}/data")
        def buffer_data(id : str = Path(..., description="unique ID of the buffer"), n : int = Query(1, description="number of samples to extract from buffer"), persistent : bool = Query(True, description="whether to keep the extracted data in the buffer or remove it on query"), with_meta : bool = Query(False, description="specifies whether to include meta data")) -> dict:
            """
            Returns the data stored in the specified buffer.
            """
            buffer : Buffer = agent.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            if with_meta:
                return buffer.data_with_meta(n, persistent)
            else:
                return buffer.data(n, persistent)
               
        @router.post("/")
        def add_buffer(buffer_def : BufferDefinition) -> str:
            buffer : Buffer = ClassUtils.create_instance(buffer_def.type)
            buffer.type = buffer_def.type
            buffer.id = buffer_def.id
            buffer.capacity = buffer_def.capacity
            buffer.data_type = buffer_def.data_type
            buffer.initial_values = buffer_def.initial_values
            buffer.unit = buffer_def.unit
            buffer.description = buffer_def.description
            agent.add_buffer(buffer)
            return buffer_def.id
        
        @router.put("/{id}")
        def add_data(id : str = Path(description="unique ID of the buffer"), data : BufferData = None)-> bool:
            if id not in agent.buffer_store:
                return {"error" : "Buffer with " + id + " not found"}
            agent.buffer_store[id].push(data.data)
            return True
               
        return router
   