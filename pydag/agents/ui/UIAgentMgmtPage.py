from dataclasses import dataclass, field

from nicegui import ui

from ...services.Service import Service
from ...buffers.Buffer import Buffer
from .UIElements import AgentElementConfigForm, UIPage


@dataclass
class UIAgentMgmtPage(UIPage):
    """ `UIPage` for configuring all relevant `AgentElement`'s in the `Agent` """
    
    path : str = field(default="/mgmt")
    
    def _render(self):
        self.create_header('Agent Management - Dashboard')                
        with ui.grid(columns=2).classes("w-full gap-2"):
            with ui.element('div'):
                ui.label(f"{Buffer.__name__}s").classes("text-2xl font-bold")
                for k, b in self.get_agent().buffer_store.items():
                    cf = AgentElementConfigForm(self, b)
                    self.add_ui_component(cf)
            with ui.element("div"):
                ui.label(f"{Service.__name__}s").classes("text-2xl font-bold")
                for k, s in self.get_agent().service_store.items():
                    cf = AgentElementConfigForm(self, s)
                    self.add_ui_component(cf)