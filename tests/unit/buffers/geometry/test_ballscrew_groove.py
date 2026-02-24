import os

import numpy as np
from pydag.buffers.geometry.BallscrewGroove import BallscrewGroove
from pydag.services.plot.PlotlifyService import PlotlifyService
from pydag.services.plot.PlotlyElements import ColorNames, PlotType, Trace


def test_000():
    
    bgr = BallscrewGroove(i=4)    
    X1, Y1, Z1 = bgr.create(resolution_1=200, resolution_2=200)
    
    bgl = BallscrewGroove(i=4, right_or_left=False)    
    X2, Y2, Z2 = bgl.create(resolution_1=200, resolution_2=200)
        
    file = os.path.dirname(__file__) + os.sep + "plotly_test_000.html"
    pdoc = PlotlifyService.surface(X1, Y1, Z1, color = ColorNames.LIGHT_BLUE.value, name="right")
    
    t2 = Trace()
    t2.set_name("left").set_type(PlotType.SURFACE)
    t2.set_x(X2).set_y(Y2).set_z(Z2)
    t2.wireframe()
    color_list = [[0, str(ColorNames.LIGHT_BLUE.value)], [1, str(ColorNames.LIGHT_BLUE.value)]]
    t2.set_colorscale(color_list)
    sc = np.zeros_like(Z2).tolist()
    t2.set_surfacecolor(sc)
            
    pdoc.get_plotlys()[0].get_traces().append(t2)
    
    pdoc.get_plotlys()[0].get_layout().set_height(1100).set_width(1700)
    pdoc.to_file(file)