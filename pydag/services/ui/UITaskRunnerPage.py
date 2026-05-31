from typing import Any
from nicegui import ui
from nicegui.element import Element

from ..Service import Service
from ..tasks.TaskRunnerService import TaskRunnerService
from .UIElements import UIPage
from .UIService import UIService

DO_FILTER : bool = False

class UITaskRunnerSubPage(UIPage):
    
    def __init__(self, service : UIService, id : str):
        super().__init__(service)
        self.task_runner_id = id
        self.path = f"/task_runner/{id}"
        self._task_service : TaskRunnerService = None
        self._result_element : Element = None
    
    def register(self):
        @ui.page(self.path)
        def page():
            self._ui_components.clear()
            self._render()
            # check all ui components if timer is required
            requires_update : bool = False
            for component in self._ui_components:
                if component.requires_update:
                    requires_update = True
                    break                    
            if requires_update:
                self._timer = ui.timer(self._refresh_interval, lambda: [
                    component.update() for component in self._ui_components if component.requires_update 
                ])
    
    def _render(self):
        self.create_header(f"{TaskRunnerService.__name__} [{self.task_runner_id}] - Dashboard")
        task_service : Service = self._service.get_agent().get_service(self.task_runner_id)
        if isinstance(task_service, TaskRunnerService):
            self._task_service = task_service
            ui.label(f"{TaskRunnerService.__name__} Description: {self._task_service.description}")
            self._create_form(self._task_service.get_input_fields())
        else:
            ui.label(f"{TaskRunnerService.__name__} [{self.task_runner_id}] not found").classes("text-red-500")

    def _render_results(self, value: Any):
        # 🧠 dict → expandable section
        if isinstance(value, dict):
            with ui.expansion('dict').classes('w-full'):
                for k, v in value.items():
                    with ui.row().classes('items-start gap-2'):
                        ui.label(f'{k}:').classes('font-bold')
                        self._render_results(v)

        # 🧠 list → vertical list
        elif isinstance(value, list):
            with ui.column().classes('pl-4 gap-1'):
                for item in value:
                    self._render_results(item)

        # 🧠 scalar → label
        else:
            ui.label(str(value))
                
    def _process_result(self, result : dict[str, Any]):
        filtered_result : dict[str, Any]
        if DO_FILTER:
            # filter for output fields only        
            output_fields = self._task_service.get_output_fields()
            filtered_result = {k: v for k, v in result.items() if k in output_fields}
        else:
            filtered_result = result
        if self._result_element:
            self._result_element.clear()
        else:
            self._result_element = ui.card().classes('w-full')
        with self._result_element:
            ui.label('Result').classes('text-xl font-bold')
            with ui.column().classes('gap-2'):
                for k, v in filtered_result.items():
                    with ui.row().classes('items-start gap-2'):
                        ui.label(f'{k}:').classes('font-bold')
                        self._render_results(v)
    
    def _create_form(self, schema: dict[str, type]):
        inputs = {}
        with ui.column().classes('gap-2 w-full'):
            # 🔁 create inputs dynamically
            for name, typ in schema.items():
                if typ is int:
                    inputs[name] = ui.number(label=name).props('step=1')
                elif typ is float:
                    inputs[name] = ui.number(label=name)
                elif typ is bool:
                    inputs[name] = ui.switch(name)
                else:
                    inputs[name] = ui.input(label=name)

            # 📤 submit button
            def submit():
                request = {}
                for name, comp in inputs.items():
                    request[name] = comp.value
                ui.notify(f'Submitted: {request}')
                result = self._task_service.run(request)
                #print(result)
                self._process_result(result)
                
            ui.button('Submit', on_click=submit)


class UITaskRunnerPage(UIPage):
    """ `UIPage` for displaying all `TaskRunnerService`'s in the `Agent`, and allowing to navigate to sub pages for each `TaskRunnerService` to display details and run tasks """
    
    path : str = "/task_runner"
    
    def __init__(self, service : UIService):
        super().__init__(service)
        self._sub_pages : dict[str, UIPage] = dict()
    
    def register(self):
        self._sync_sub_pages()
        for sub_page in self._sub_pages.values():
            sub_page.register()
        
        @ui.page(self.path)
        def page():
            self._ui_components.clear()
            self._render()
            # check all ui components if timer is required
            requires_update : bool = False
            for component in self._ui_components:
                if component.requires_update:
                    requires_update = True
                    break                    
            if requires_update:
                self._timer = ui.timer(self._refresh_interval, lambda: [
                    component.update() for component in self._ui_components if component.requires_update 
                ])
    
    def _render(self):
        self._sync_sub_pages()
        self._create_main_page()
    
    def _create_main_page(self):
        # find all task runner services and display them as cards with link to sub page
        services : list[Service] = self._service.get_agent().get_services(TaskRunnerService)
        self.create_header(f"{TaskRunnerService.__name__} - Dashboard")
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

    def _sync_sub_pages(self):
        for service in self._service.get_agent().get_services(TaskRunnerService):
            if service.id not in self._sub_pages:
                self._create_sub_page(service.id)
