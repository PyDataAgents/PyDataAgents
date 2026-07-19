from typing import Any

from nicegui import ui

from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.Buffer import Buffer
from pydag.buffers.DictBuffer import DictBuffer
from pydag.agents.ui.UIElements import BufferTable, UIPage

class SubmitFormPage(UIPage):
    """ `UIPage` for diplaying a submit form that serves data to a referenced `Buffer` in `Agent` """
    
    path = "/form_test"
    
    def __init__(self, agent : Agent, buffer : Buffer):
        super().__init__(agent)
        self._buffer : Buffer = buffer
            
    def _handle_submit(self, data : dict[str, Any]):
        self._buffer.push(data)
        ui.notify("Submitted!", position="bottom", type="positive")
        
    def _render(self):
        with ui.header().classes('bg-primary text-white'):
            ui.label('Submitform - Test Page').classes('font-bold text-lg')
    
        surname = ui.input(label='Surname')
        name = ui.input(label='Name')
        age = ui.number(label='Age')
        email = ui.input(label='Email')
        
        def on_submit():
            data = {
                "surname": surname.value,
                "name": name.value,
                "age": age.value,
                "email": email.value,
            }
            self._handle_submit(data)
            
            # Clear inputs
            surname.value = ""
            name.value = ""
            age.value = None
            email.value = ""
            
        bt = BufferTable(self, self._buffer)
        self.add_ui_component(bt)
        
        ui.button('Submit', on_click=on_submit)
            

def test_000():
    ag = Agent()
    
    buf = DictBuffer()   
    ag.add_buffer(buf)
    
    sp = SubmitFormPage(ag, buf)
    
    app = AgentApp(port=8081, with_ui=True, with_api=False, dark_mode=False)
    app.set_agent(ag)
    app.add_ui_page(sp)
    app.create()
    app.run()