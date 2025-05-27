from fastapi import APIRouter, Path, Query
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.grabbers.Grabber import Grabber

ROOT_URL : str = "/api/v1/buffers"

class BufferRESTAPI:
    """
    REST API for Buffers using FastAPI.
    Provides endpoints to interact with the buffer instances.
    """
   
    @staticmethod
    def get_api_router(grabber : Grabber) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["Buffers"],)
        
        @router.get("/")
        def buffers() -> list[str]:
            """
            Returns a list of all available buffer IDs.
            """
            return list(grabber.buffer_store.keys())
        
        @router.get("/config")
        def buffer_config(with_sizes : bool = Query(False, description="specifies whether to return the current size on top of configurations")):
            """
            Returns a list of all buffer configurations.
            """
            li = list()
            for buffer in grabber.buffer_store.values():
                d = buffer.config_options()
                if with_sizes:
                    d["size"] = buffer.size()
                li.append(d)
            return li
                
        @router.get("/{id}")
        def buffer(id : str = Path(..., description="unique ID of the buffer")):
            buffer : Buffer = grabber.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            return buffer.config_options()
        
        @router.get("/{id}/size")
        def buffer_size(id : str = Path(..., description="unique ID of the buffer")):
            """
            Returns the size of the specified buffer.
            """
            buffer : Buffer = grabber.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            return buffer.size()
        
        @router.get("/{id}/data")
        def buffer_data(id : str = Path(..., description="unique ID of the buffer"), n : int = Query(1, description="number of samples to extract from buffer"), persistent : bool = Query(True, description="whether to keep the extracted data in the buffer or remove it on query")):
            """
            Returns the data stored in the specified buffer.
            """
            buffer : Buffer = grabber.get_buffer(id)
            if buffer is None:
                return {"error": "Buffer not found"}
            return buffer.data(n, persistent)
        
        @router.post("/")
        def add_buffer(d : dict) -> str:
            
            return d["id"]
        
               
        return router