from fastapi import APIRouter

from ...agents.Agent import Agent
from ..tasks.TaskRunnerService import TaskRunnerService


ROOT_URL : str = "/api/v1/tasks"


class TaskRestAPI():
    """
    REST API for executing tasks using FastAPI.
    Provides endpoints to interact with `TaskRunnerService` instance.
    """

    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[TaskRunnerService.__name__])
        
        @router.get("/")
        def tasks():
            return True