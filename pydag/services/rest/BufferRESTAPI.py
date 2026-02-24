from typing import Any, Dict, List, Union
from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field

from ...buffers.DictBuffer import DictBuffer
from ...agents.AgentConfig import AgentConfig
from ...utils.DataUtils import DataUtils
from ...buffers.Buffer import Buffer
from ...buffers.DataType import DataType
from ...agents.Agent import Agent
from ...utils.ClassUtils import ClassUtils

ROOT_URL : str = "/api/v1/buffers"
 
class BufferDefinition(BaseModel):
    type : str = Field(default=DictBuffer.__module__, title="type of the buffer to create")
    id : str = Field(default=DictBuffer().unique_id(), title="unique identifer throughout agent application")
    capacity : int = Field(default=1, title="number of elements that can be stored in buffer before being discarded in FiFo fashion")
    data_type : str = Field(default=DataType.FLOAT.value, title="datatype to expect from buffer elements, can be DataType enum or list of enums")
    initial_values : Any = Field(default=None, title="initial values in buffer")
    unit : Any = Field(default=None, title="unit of element values in this buffer, can be string or list of strings")
    description : str = Field(default=None, title="buffer description")

class DictBufferDefinition(BufferDefinition):
    timestamps_enabled : bool = Field(default=False, title="Whether timestamps are enabled for this buffer.")
    timestamps_key  : str = Field(default="timestamps", title="Key under which timestamps are exposed.")
    index_enabled : bool = Field(default=False, title="Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point.")
    index_key : str = Field(default="index", title="Key name for index column.")


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
        def buffer_type(type : str = Query(..., description="specifies the fully qualified name of the buffer type")) -> dict:
            """
            Returns the specifieds buffer default configuration.
            """
            buffer = ClassUtils.create_instance(type)
            if buffer is None:
                return {}
            elif isinstance(buffer, Buffer):
                return buffer.config_options(with_descriptions=True)
            else:
                return {}
        
        @router.get("/configs")
        def buffer_configs(with_sizes : bool = Query(False, description="specifies whether to return the current size on top of configurations")) -> list:
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
        
        @router.get("/available")
        def available_buffers() -> list[str]:            
            """ returns a list of buffer package names, that can be created            
            """
            return ClassUtils.get_subclasses(Buffer) 
        
        @router.get("/usage")
        def buffer_usage(type : str = Query(..., description="type of the buffer (fully qualified package name)")) -> str:
            """
            Returns the usage information for specified `Buffer` type contained in the doc string of the class.
            """
            buffer = ClassUtils.create_instance(type)
            if buffer is None:
                return None
            elif isinstance(buffer, Buffer):
                return buffer.__doc__.strip()
            else:
                return None
                
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
        def buffer_data(id : str = Path(..., description="unique ID of the buffer"), n : int = Query(0, description="number of samples to extract from buffer"), persistent : bool = Query(True, description="whether to keep the extracted data in the buffer or remove it on query"), with_meta : bool = Query(False, description="specifies whether to include meta data"), by_rows : bool = Query(False, description="specifies whether to return the data as list of dictionaries instead of a dictionary of lists, defaults to False")) -> Union[Dict|List]:
            """
            Returns the data stored in the specified buffer.
            """
            buffer : Buffer = agent.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            if with_meta:
                mdata = buffer.data_with_meta(n, persistent)
                if mdata is None:
                    return {}
                data = mdata[AgentConfig.DATA]
                if by_rows:
                    mdata[AgentConfig.DATA] = DataUtils.dict_to_list(data)
                DataUtils.serialize_dict(mdata)
                return mdata
            else:
                data = buffer.data(n, persistent)
                if data is None:
                    return {}
                DataUtils.serialize_dict(data)
                if by_rows:
                    return DataUtils.dict_to_list(data)
                else:
                    return data
               
        @router.post("/")
        def add_buffer(buffer_def : Union[BufferDefinition, DictBufferDefinition]) -> str:
            buffer : Buffer = ClassUtils.create_instance(buffer_def.type)
            ClassUtils.set_properties(buffer, buffer_def.model_dump())
            agent.add_buffer(buffer)
            return buffer_def.id
        
        @router.put("/{id}/data")
        def add_data(id : str = Path(description="unique ID of the buffer"), data : BufferData = None)-> bool:
            if id not in agent.buffer_store:
                return False
            agent.get_buffer(id).push(data.data)
            return True
        
        @router.delete("/{id}/data")
        def clear_data(id : str = Path(description="unique ID of the buffer"))-> bool:
            if id not in agent.buffer_store:
                return False
            agent.get_buffer(id).clear()
            return True
               
        return router
   