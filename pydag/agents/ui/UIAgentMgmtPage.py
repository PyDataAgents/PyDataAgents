from nicegui import ui


from ...nodes.Node import Node
from ...agents.AgentElement import AgentElement
from ...services.Service import Service
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
                for k, b in self.get_agent().buffer_store.items():
                    cf = AgentElementConfigForm(self, b)
                    self.add_ui_component(cf)
            with ui.element("div"):
                ui.label(f"{Service.__name__}s").classes("text-2xl font-bold")
                for k, s in self.get_agent().service_store.items():
                    cf = AgentElementConfigForm(self, s)
                    self.add_ui_component(cf)
        
        # Function to handle form submission
        def submit_form():
            ui.notify(f'type: {type.value}, Email: {email.value}')
            dialog.close()

        # Create dialog (modal)
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Create new {AgentElement.__name__}")

            radio = ui.radio(
                options=[f"{Buffer.__name__}", f"{Service.__name__}", f"{Node.__name__}"],
                value=f"{Buffer.__name__}"
            )
            
            type = ui.input('Name')
            email = ui.input('Email')

            with ui.row():
                ui.button('Submit', on_click=submit_form)
                ui.button('Cancel', on_click=dialog.close)

        # Button to open dialog
        ui.button(f"Create new {AgentElement.__name__}", on_click=dialog.open)