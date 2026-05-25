from nicegui import ui

from ..Service import Service
from ...buffers.Buffer import Buffer
from .UIElements import AgentElementConfigForm, UIPage


class UIAgentMgmtPage(UIPage):
    """ `UIPage` for configuring all relevant `AgentElement`'s in the `Agent` """
    
    path = "/mgmt"
    
    def _render(self):
        self.create_header('Agent Management - Dashboard')                
        with ui.grid(columns=2).classes("w-full gap-2"):
            with ui.element('div'):
                ui.label(f"{Buffer.__name__}s").classes("text-2xl font-bold")
                for k, b in self._service.get_agent().buffer_store.items():
                    cf = AgentElementConfigForm(self, b)
                    self.add_ui_component(cf)
            with ui.element('div'):
                ui.label(f"{Service.__name__}s").classes("text-2xl font-bold")
                for k, s in self._service.get_agent().service_store.items():
                    cf = AgentElementConfigForm(self, s)
                    self.add_ui_component(cf)