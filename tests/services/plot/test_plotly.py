import json
import os

import numpy as np
from pydag.services.plot.PlotlyElements import Layout, Mode, PlotType, Plotly, PlotlyDocument, Trace
from pydag.utils.MathUtils import MathUtils


def test_000():
    t = Trace()
    t.x = [1.0, 2.0, 3.0, 4.0]
    t.y = [1.0, 1.1, 1.2, 1.3]
    
    print(t)
    print(t.__dict__)
    
    print(json.dumps(t.to_dict()))
    
def test_001():
    t = Trace()
    t.x = [1.0, 2.0, 3.0, 4.0]
    t.set_w(np.linspace(0, 10, 100))
    print(t.to_dict())
    
def test_010():
    
    p = Plotly()
    t = Trace()
    t.x = [1.0, 2.0, 3.0, 4.0]
    t.y = [1.0, 1.1, 1.2, 1.3]
    p.get_traces().append(t)
    print(p.to_dict())
    
def test_020():
    p = Plotly()
    t = Trace()
    t.x = [1.0, 2.0, 3.0, 4.0]
    t.y = [1.0, 1.1, 1.2, 1.3]
    p.get_traces().append(t)
    pdoc = PlotlyDocument(p)
    pdoc.to_file("tests" + os.sep + "services" + os.sep + "plot" + os.sep + "plotly_test_020.html")
    
def test_021():
    p = Plotly()
    t = Trace()
    t.x = [1.0, 2.0, 3.0, 4.0]
    t.y = [1.0, 1.1, 1.2, 1.3]
    t.set_type(PlotType.SCATTER)
    t.set_mode(Mode.LINES_MARKERS)
    
    p.get_traces().append(t)
    
    l = Layout()
    l.set_height(800)
    l.set_width(1600)
    p.set_layout(l)
    
    pdoc = PlotlyDocument(p)
    pdoc.to_file("tests" + os.sep + "services" + os.sep + "plot" + os.sep + "plotly_test_021.html")
    
def test_030():    
    x, y = MathUtils.circle()
    p = Plotly()
    t = Trace()
    t.set_x(x)
    t.set_y(y)
    t.set_type(PlotType.SCATTER)
    t.set_mode(Mode.LINES_MARKERS)
    p.get_traces().append(t)
    p.get_layout().equal_axis()
    pdoc = PlotlyDocument(p)
    pdoc.to_file("tests" + os.sep + "services" + os.sep + "plot" + os.sep + "plotly_test_030.html")
    
    