from __future__ import annotations
from fastapi import APIRouter, Path, Query
from loguru import logger

from ...agents.Agent import Agent
from ..langchain.LLMSQLService import LLMSQLService
from ..langchain.LLMService import LLMService
from ..langchain.RAGService import RAGService

ROOT_URL : str = "/api/v1/llm"

class LLMRestAPI:
    """
    REST API for LLM Service access via HTTP Requests using FastAPI.
    Provides endpoints to interact with LLM Models for Chat, RAG or SQL Q&A
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=["LLM"],)
        
        @router.get("/")
        def llm_services():
            """returns the id's of all LLMservices in this Agent instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in agent.service_store.values():
                if isinstance(service, LLMService) and not isinstance(service, RAGService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/sql")
        def llm_sql_services():
            """returns the id's of all LLMSQLServices in this Agent instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in agent.service_store.values():
                if isinstance(service, LLMService) and not isinstance(service, RAGService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/rag")
        def rag_services():
            """returns the id's of all RAGServices in this Agent instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in agent.service_store.values():
                if isinstance(service, RAGService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/{service_id}/chat")
        def chat(service_id : str = Path(..., description="unique id of the LLM service"), question : str = Query(..., description="prompt for the LLM to answer to")) -> str:
            """
            returns an answer to the question being asked
            """
            if service_id in agent.service_store:
                if isinstance(agent.service_store[service_id], LLMService):
                    llm_service : LLMService = agent.service_store[service_id]
                    return llm_service.chat(question)
                else:
                    logger.error("Service with id=" + service_id + " is not of type " + LLMService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + LLMService.cname() + " found"}
            else:
                logger.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
        
        @router.get("/rag/{service_id}/chat")
        def rag_chat(service_id : str = Path(..., description="unique id of the RAG service"), question : str = Query(..., description="prompt for the RAG engine to answer to")) -> str:
            """
            returns an answer to the question being asked
            """
            if service_id in agent.service_store:
                if isinstance(agent.service_store[service_id], RAGService):
                    rag_service : RAGService = agent.service_store[service_id]
                    return rag_service.chat(question)
                else:
                    logger.error("Service with id=" + service_id + " is not of type " + RAGService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + RAGService.cname() + " found"}
            else:
                logger.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
        
        @router.put("/rag/{service_id}/document")
        def rag_document(service_id : str = Path(..., description="unique id of the RAG service"), link : str = Query(..., description="link to the document to add to RAG engine")):
            if service_id in agent.service_store:
                if isinstance(agent.service_store[service_id], RAGService):
                    rag_service : RAGService = agent.service_store[service_id]
                    rag_service.add_document(link)
                    return {"success": "Document " + link + " was added to " + RAGService.cname() + " with id=" + service_id}
                else:
                    logger.error("Service with id=" + service_id + " is not of type " + RAGService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + RAGService.cname() + " found"}
            else:
                logger.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
        
        @router.get("/sql/{service_id}/chat")
        def sql_chat(service_id : str = Path(..., description="unique id of the LLMSQLService"), question : str = Query(..., description="question for the SQL LLM engine to answer")) -> dict:
            if service_id in agent.service_store:
                if isinstance(agent.service_store[service_id], LLMSQLService):
                    sql_service : LLMSQLService = agent.service_store[service_id]
                    return sql_service.chat(question)
                else:
                    logger.error("Service with id=" + service_id + " is not of type " + LLMSQLService.cname() + " found")    
                    return {"error": "Service with id=" + service_id + " is not of type " + LLMSQLService.cname() + " found"}
            else:
                logger.error("No Service with id=" + service_id + " was found")    
                return {"error": "No Service with id=" + service_id + " was found"}
                          
        return router
    