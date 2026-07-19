from nicegui import ui

from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.RandBoolean import RandBoolean
from pydag.agents.ui.UIElements import TrafficLight, UIPage


class TrafficLightPage(UIPage):
    """ `UIPage` for diplaying all `Buffer` data from connected `Agent` """
    
    path = "/traffic_light"
    buffer_id = "B1"
        
    def _render(self):
        with ui.header().classes('bg-primary text-white'):
            ui.label('Traffic Light - Test Page').classes('font-bold text-lg')
        
        if self.buffer_id in self.get_agent().buffer_store:
            buffer = self.get_agent().buffer_store[self.buffer_id]
            t = TrafficLight(self, buffer, ["values"])
            self.add_ui_component(t)

def test_000():
    ag = Agent()
    
    s1 = RandBoolean()
    buf = SignalBuffer(id="B1", signal=s1, capacity=1, sampling_period=1000)    
    ag.add_buffer(buf)
    
    tp = TrafficLightPage(ag)
    tp.buffer_id = "B1"
    
    app = AgentApp(port=8081, with_ui=True, with_api=False, dark_mode=False)
    app.set_agent(ag)
    app.add_ui_page(tp)
    app.create()
    app.run()