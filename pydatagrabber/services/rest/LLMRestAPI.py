from __future__ import annotations
from fastapi import APIRouter, Path, Query

from ...grabbers.Grabber import Grabber

ROOT_URL : str = "/api/v1/llm"

class LLMRestAPI:
    """
    REST API for Excel Table access via HTTP Requests using FastAPI.
    Provides endpoints to read from named excel tables inside a excel file.
    """
   
    @staticmethod
    def get_api_router(grabber : Grabber) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["Excel"],)
        
        @router.get("/chat/{service_id}")
        def chat(service_id : str = Path(..., description="unique id of the llm service"), question : str = Query(..., description="prompt for the llm to answer to")) -> str:
            """
            returns an answer to the question being asked
            """
            return ""
                              
        return router