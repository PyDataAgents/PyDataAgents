import os
from pydag.buffers.geometry.Helix import Helix
from pydag.services.plot.PlotlifyService import PlotlifyService


def test_000():
    
    h = Helix(i=2)
    
    x, y, z = h.create()
    
    file = os.path.dirname(__file__) + os.sep + "plotly_test_000.html"
    PlotlifyService.line(x, y, z).to_file(file)