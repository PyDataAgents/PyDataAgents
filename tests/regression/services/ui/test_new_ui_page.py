from nicegui import ui

from pydag.agents.Agent import Agent
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.RandBoolean import RandBoolean
from pydag.services.ui.UIElements import TrafficLight, UIPage
from pydag.services.ui.UIService import UIService


class TrafficLightPage(UIPage):
    """ `UIPage` for diplaying all `Buffer` data from connected `Agent` """
    
    path = "/traffic_light"
    buffer_id = "B1"
        
    def _render(self):
        with ui.header().classes('bg-primary text-white'):
            ui.label('Traffic Light - Test Page').classes('font-bold text-lg')
        
        if self.buffer_id in self._service.get_agent().buffer_store:
            buffer = self._service.get_agent().buffer_store[self.buffer_id]
            t = TrafficLight(self, buffer, ["values"])
            self.add_ui_component(t)

def test_000():
    ag = Agent()
    
    s1 = RandBoolean()
    buf = SignalBuffer(id="B1", signal=s1, capacity=1, sampling_period=1000)    
    ag.add_buffer(buf)
    
    uis = UIService(refresh_interval=1.0/30.0)
    tp = TrafficLightPage(uis)
    tp.buffer_id = "B1"
    uis.add_page(tp)
    ag.add_service(uis)
    
    ag.release()