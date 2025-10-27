import os
from pydag.services.plot.PlotlifyService import PlotlifyService


def test_000():    
    x = [1.0, 2.0, 3.0, 4.0]
    y = [1.0, 1.1, 1.2, 1.3]
    
    PlotlifyService.area(x=x, y=y).to_file(os.path.dirname(__file__) + os.sep + "plotlifyservice_test_000.html")