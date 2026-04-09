from __future__ import annotations
from fastapi import APIRouter, Body, HTTPException, Path


from ..Service import Service
from ...agents.Agent import Agent
from .DataModelService import DataModelService

ROOT_URL : str = "/api/v1/datamodelservices"

class DataModelRestAPI:
    """
    REST API for DataModelService access via HTTP Requests using FastAPI.
    Provides endpoints to interact with DataModels
    """
   
    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[DataModelService.__name__])
        
        @router.get("/")
        def datamodel_services():
            """returns the id's of all DataModelServices in this Agent instance

            Returns:
                list[str]: list of strings
            """
            service_ids = list()
            for service in agent.get_services(DataModelService):
                if isinstance(service, DataModelService):
                    service_ids.append(service.id)
            return service_ids
        
        @router.get("/{service_id}/session")
        def create_session(service_id: str = Path(..., description="id of the DataModel Service")) -> str:
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                session_id = service.create_session()
                return session_id
            else:
                raise HTTPException(status_code=404, detail=f"No {Service.__name__} with specified id {service_id} was found")            
        
        @router.get("/{service_id}/sessions")
        def get_sessions(service_id: str = Path(..., description="id of the DataModel Service")) -> dict[str, int]:
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                sessions : dict = service.get_sessions()
                return sessions
            else:
                raise HTTPException(status_code=404, detail=f"No {Service.__name__} with specified id {service_id} was found")
        
        @router.get("/{service_id}/session/{session_id}/models")
        def datamodels(service_id : str = Path(..., description="id of the DataModel Service"), session_id : str = Path(..., description="id of the session with the models")) -> list[str]:
            """returns the id's of all DataModels inside the specified Session of a DataModelService

            Args:
                service_id (str): id of the DataModel Service
                session_id (str): id of the Session

            Returns:
                list[str]: list of strings
            """
            datamodel_ids = list()
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                datamodel_ids = service.get_data_models(session_id)
            return datamodel_ids
                    
        @router.put("/{service_id}/session/{session_id}/model/{model_id}")
        async def update_model(service_id : str = Path(..., description="id of the DataModel Service"), session_id : str = Path(..., description="id of the session with the models") , model_id : str = Path(..., description="id of the DataModel to update"), data : dict = Body(..., description="new data for the DataModel")):
            """updates the DataModel with the given model_id and session_id of the DataModelService with the given service_id with the provided data

            Args:
                service_id (str): id of the DataModel Service
                session_id (str): id of the session of the models
                model_id (str): id of the DataModel to update
                data (dict): new data for the DataModel

            Returns:
                dict: updated DataModel as dict
            """
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                await service.updates(session_id, model_id, data)
                model = service.get_data_model(session_id, model_id)
                return model.to_dict() if model else {}
            return {}
        
        @router.get("/{service_id}/session/{session_id}/models/{model_id}")
        def get_model_data(service_id : str = Path(..., description="id of the DataModel Service"), session_id : str = Path(..., description="id of the session with the models"), model_id : str = Path(..., description="id of the DataModel to get")):
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                model = service.get_data_model(session_id, model_id)
                if model:
                    return model.to_dict()
            return {}
        
        @router.get("/{service_id}/source")
        def get_model_source(service_id : str = Path(..., description="id of the DataModel Service")) -> str:
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                src = service.get_source()
                return src
            return ""
        
        return router