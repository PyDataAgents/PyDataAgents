from __future__ import annotations
from fastapi import APIRouter, Path, Query
from loguru import logger

from ...services.LLMService import LLMService
from ...services.RAGService import RAGService
from ...grabbers.Grabber import Grabber

ROOT_URL : str = "/api/v1/llm"
LOGGER = logger

class LLMRestAPI:
    """
    REST API for Excel Table access via HTTP Requests using FastAPI.
    Provides endpoints to read from named excel tables inside a excel file.
    """
   
    @staticmethod
    def get_api_router(grabber : Grabber) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["LLM"],)
        
        @router.get("/")
        def llm_services():
            """returns the id's of all LLMservices in this Grabber instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in grabber.service_store.values():
                if isinstance(service, LLMService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/rag")
        def rag_services():
            """returns the id's of all RAGServices in this Grabber instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in grabber.service_store.values():
                if isinstance(service, RAGService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/chat/{service_id}")
        def chat(service_id : str = Path(..., description="unique id of the LLM service"), question : str = Query(..., description="prompt for the LLM to answer to")) -> dict:
            """
            returns an answer to the question being asked
            """
            if service_id in grabber.service_store:
                if isinstance(grabber.service_store[service_id], LLMService):
                    llm_service : LLMService = grabber.service_store[service_id]
                    return llm_service.chat(question)
                else:
                    LOGGER.error("Service with id=" + service_id + " is not of type " + LLMService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + LLMService.cname() + " found"}
            else:
                LOGGER.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
        
        @router.get("/rag/chat/{service_id}")
        def rag_chat(service_id : str = Path(..., description="unique id of the RAG service"), question : str = Query(..., description="prompt for the RAG engine to answer to")) -> dict:
            """
            returns an answer to the question being asked
            """
            if service_id in grabber.service_store:
                if isinstance(grabber.service_store[service_id], RAGService):
                    rag_service : RAGService = grabber.service_store[service_id]
                    return rag_service.chat(question)
                else:
                    LOGGER.error("Service with id=" + service_id + " is not of type " + RAGService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + RAGService.cname() + " found"}
            else:
                LOGGER.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
        
        @router.put("/rag/{service_id}/document")
        def rag_document(service_id : str = Path(..., description="unique id of the RAG service"), document_link : str = Query(..., description="link to the document to add to RAG engine")):
            if service_id in grabber.service_store:
                if isinstance(grabber.service_store[service_id], RAGService):
                    rag_service : RAGService = grabber.service_store[service_id]
                    rag_service.add_document(document_link)
                    return {"success": "Document " + document_link + " was added to " + RAGService.cname() + " with id=" + service_id}
                else:
                    LOGGER.error("Service with id=" + service_id + " is not of type " + RAGService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + RAGService.cname() + " found"}
            else:
                LOGGER.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
                          
        return router
    