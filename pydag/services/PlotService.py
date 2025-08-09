import dash
from .Service import Service


class PlotService(Service):
    
    def __init__(self):
        super().__init__()
        self.app : dash.Dash = None
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    @staticmethod
    def generate_gauge_callback(gauge_id):
        pass
    
    @staticmethod
    def generate_line_plot_callback(plot_id):
        pass