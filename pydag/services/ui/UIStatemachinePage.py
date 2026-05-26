from typing import Any
from nicegui import ui
from nicegui.element import Element


from ...nodes.triggers.ObserverTriggerAction import ObserverTriggerAction
from ...nodes.Node import Node
from ...services.statemachine.StatemachineService import StatemachineService
from ..Service import Service
from .UIElements import UIPage
from .UIService import UIService


class UIStatemachineSubPage(UIPage):
    """ `UIPage` for displaying a single `StatemachineService` with config details and trigger execution """
    
    def __init__(self, service : UIService, id : str):
        super().__init__(service)
        self.statemachine_id = id
        self.path = f"/statemachines/{id}"
        self._statemachine_service : StatemachineService = None
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
        self.create_header(f"{StatemachineService.__name__} [{self.statemachine_id}] - Dashboard")
        statemachine_service : Service = self._service.get_agent().get_service(self.statemachine_id)
        if isinstance(statemachine_service, StatemachineService):
            self._statemachine_service = statemachine_service
            ui.label(f"{StatemachineService.__name__} Description: {self._statemachine_service.description}").classes("text-sm text-gray-500")
            self._create_form()
        else:
            ui.label(f"{StatemachineService.__name__} [{self.statemachine_id}] not found").classes("text-red-500")

    def _create_form(self):
        schema = {}
        inputs = {}
        nodes : dict[str, Node] = self._statemachine_service.nodes
        trigger_node : Node = None
        for node in nodes.values():
            if isinstance(node, ObserverTriggerAction):
                trigger_node = node
                break
        if trigger_node is None:
            ui.label(f"No {ObserverTriggerAction.__name__} found in {StatemachineService.__name__} [{self.statemachine_id}]").classes("text-red-500")
            return
        else:
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

                # 📤 start trigger button
                def start_trigger():
                    request = {}
                    for name, comp in inputs.items():
                        request[name] = comp.value
                    ui.notify(f'Submitted: Trigger for {Node.__name__} [{trigger_node.id}] with config request:{request}')
                    trigger_node.trigger()
                    
                ui.button('Start', on_click=start_trigger)


class UIStatemachinePage(UIPage):
    """ `UIPage` for displaying all `StatemachineService`'s in the `Agent`
    and allowing to navigate to sub pages for each `StatemachineService` to 
    display config details and trigger execution """
    
    path : str = "/statemachines"
    
    def __init__(self, service : UIService):
        super().__init__(service)
        self._sub_pages : dict[str, UIPage] = dict()
    
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
            # register sub pages
            for sub_page in self._sub_pages.values():
                sub_page.register()
    
    def _render(self):
        self._create_main_page()
        for service in self._service.get_agent().get_services(StatemachineService):
            if service.id not in self._sub_pages:
                self._create_sub_page(service.id)
    
    def _create_main_page(self):
        # find all task runner services and display them as cards with link to sub page
        services : list[Service] = self._service.get_agent().get_services(StatemachineService)
        self.create_header(f"{StatemachineService.__name__} - Dashboard")
        with ui.grid(columns=4).classes('gap-4'):
            for service in services:
                if isinstance(service, StatemachineService):
                    link = {"title": f"{StatemachineService.__name__} [{service.id}]", "url": f"/statemachines/{service.id}"}
                    with ui.card().classes('p-4 cursor-pointer'):
                        ui.link(link["title"], target=link["url"])
                        if service.description:
                            ui.label(service.description).classes("text-sm text-gray-500")
    
    def _create_sub_page(self, id : str):
        sub_page : UIPage = UIStatemachineSubPage(self._service, id)
        self._sub_pages[id] = sub_page      