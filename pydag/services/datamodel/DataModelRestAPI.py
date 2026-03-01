from __future__ import annotations
from fastapi import APIRouter, Body, Path, Query
from loguru import logger

from ...agents.Agent import Agent
from ...services.datamodel.DataModelService import DataModelService

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
        
        @router.get("/{service_id}/models")
        def datamodels(service_id : str = Path(..., description="id of the DataModel Service")):
            """returns the id's of all DataModels of a DataModelService

            Args:
                service_id (str): id of the DataModel Service

            Returns:
                list[str]: list of strings
            """
            datamodel_ids = list()
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                datamodel_ids = list(service.get_data_models().keys())
            return datamodel_ids
        
        @router.put("/{service_id}/models/{model_id}")
        def update_model(service_id : str = Path(..., description="id of the DataModel Service"), model_id : str = Path(..., description="id of the DataModel to update"), data : dict = Body(..., description="new data for the DataModel")):
            """updates the DataModel with the given model_id of the DataModelService with the given service_id with the provided data

            Args:
                service_id (str): id of the DataModel Service
                model_id (str): id of the DataModel to update
                data (dict): new data for the DataModel

            Returns:
                dict: updated DataModel as dict
            """
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                service.updates(model_id, data)
                model = service.get_data_model(model_id)
                return model.to_dict() if model else {}
            return {}
        
        @router.get("/{service_id}/models/{model_id}")
        def get_model_data(service_id : str = Path(..., description="id of the DataModel Service"), model_id : str = Path(..., description="id of the DataModel to get")):
            service = agent.get_service(service_id)
            if service and isinstance(service, DataModelService):
                model = service.get_data_model(model_id)
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