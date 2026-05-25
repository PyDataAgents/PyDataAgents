from typing import Any

from fastapi import APIRouter, Body, Path, HTTPException

from pydag.services.Service import Service

from ...agents.Agent import Agent
from ..tasks.TaskRunnerService import TaskRunnerService


ROOT_URL : str = "/api/v1/taskrunners"


class TaskRestAPI():
    """
    REST API for executing tasks using FastAPI.
    Provides endpoints to interact with `TaskRunnerService` instance.
    """

    @staticmethod
    def get_api_router(agent : Agent) -> APIRouter:
        
        router = APIRouter(prefix=ROOT_URL, tags=[TaskRunnerService.__name__])
        
        @router.get("/")
        def task_runners() -> list[Service]:
            return agent.get_services(TaskRunnerService.__class__)
        
        @router.put("/{id}/run")
        def run_taskrunner(id : str = Path(description=""), data : dict[str, Any] = Body(..., description="")) -> dict[str, Any]:
            service : TaskRunnerService = agent.get_service(id)
            if isinstance(service, TaskRunnerService):
                return service.run(data)
            else:
                raise HTTPException(status_code=404, detail=f"TaskRunnerService with id '{id}' not found")
            