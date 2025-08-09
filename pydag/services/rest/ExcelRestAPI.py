from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import APIRouter, Path
if TYPE_CHECKING:
    from .ExcelRestService import ExcelRestService

ROOT_URL : str = "/api/v1/excel_tables"

class ExcelRestAPI:
    """
    REST API for Excel Table access via HTTP Requests using FastAPI.
    Provides endpoints to read from named excel tables inside a excel file.
    """
   
    @staticmethod
    def get_api_router(excel_rest_service : ExcelRestService) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["Excel"],)
        
        @router.get("/")
        def tables() -> list[str]:
            """
            Returns a list of all named tables in the specified ExcelRestService
            """
            return excel_rest_service.named_tables.keys()
        
        @router.get("/{name}")
        def table_data(name : str = Path(..., description="unique name of the table")) -> dict:
            if name in excel_rest_service.named_tables:
                return excel_rest_service.named_tables[name].data()
            else:
                return {"error": "Table " + name + " not found"}
                       
        return router