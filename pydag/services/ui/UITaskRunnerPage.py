from nicegui import ui

from ..Service import Service
from ..tasks.TaskRunnerService import TaskRunnerService
from .UIElements import UIPage
from .UIService import UIService


class UITaskRunnerSubPage(UIPage):
    
    def __init__(self, service : UIService, id : str):
        super().__init__(service)
        self.task_runner_id = id
        self.path = f"/task_runner/{id}"
    
    def _render(self):
        pass

class UITaskRunnerPage(UIPage):
    
    path : str = "/task_runner"
    
    def __init__(self, service : UIService):
        super().__init__(service)
        self._sub_pages : dict[str, UIPage] = dict()
    
    def _render(self):
        self._create_main_page()
        for service in self._service.get_agent().get_services(TaskRunnerService):
            if service.id not in self._sub_pages:
                self._create_sub_page(service.id)
    
    def _create_main_page(self):
        # find all task runner services and display them as cards with link to sub page
        services : list[Service] = self._service.get_agent().get_services(TaskRunnerService)
        with ui.header().classes('bg-primary text-white'):
            ui.label(f"{TaskRunnerService.__name__} - Dashboard").classes('font-bold text-lg')
        with ui.grid(columns=4).classes('gap-4'):
            for service in services:
                if isinstance(service, TaskRunnerService):
                    link = {"title": f"TaskRunner {service.id}", "url": f"/task_runner/{service.id}"}
                    with ui.card().classes('p-4 cursor-pointer'):
                        ui.link(link["title"], target=link["url"])
                        if service.description:
                            ui.label(service.description).classes("text-sm text-gray-500")
    
    def _create_sub_page(self, id : str):
        sub_page : UIPage = UITaskRunnerSubPage(self._service, id)
        self._sub_pages[id] = sub_page