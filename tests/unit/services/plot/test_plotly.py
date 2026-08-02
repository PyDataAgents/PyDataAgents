import json
import os

import numpy as np
from pydag.services.plot.PlotlyElements import Layout, Mode, PlotType, Plotly, PlotlyDocument, Trace, Color
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
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_020.html")
    
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
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_021.html")
    
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
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_030.html")
    
def test_031():    
    x, y = MathUtils.circle()
    p = Plotly()
    t = Trace()
    t.set_x(x)
    t.set_y(y)
    t.set_type(PlotType.SCATTER)
    t.set_mode(Mode.LINES_MARKERS)
    p.get_traces().append(t)
    
    x2, y2 = MathUtils.circle(1.2, 0.1, 0.1)
    t2 = Trace()
    t2.set_x(x2)
    t2.set_y(y2)
    t2.set_type(PlotType.SCATTER)
    t2.set_mode(Mode.LINES_MARKERS)
    p.get_traces().append(t2)
    
    p.get_layout().equal_axis()
    pdoc = PlotlyDocument(p)
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_031.html")
    
def test_040():
    p = Plotly()
    t1 = Trace()
    t1.x = [1.0, 2.0, 3.0, 4.0]
    t1.y = [1.0, 1.1, 1.2, 1.3]
    
    t2 = Trace()
    t2.x = [1.0, 2.0, 3.0, 4.0]
    t2.y = [1.0, 2.1, 0.2, 1.3]
    
    p.get_traces().append(t1)
    p.get_traces().append(t2)
    
    p.get_layout().get_grid().set_rows(1).set_columns(2).set_pattern("independent")
    p.subplots()
    pdoc = PlotlyDocument(p)
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_040.html")
    
def test_050():
    
    lt = {
        "title": {
            "text": "test title"
        },
        "xaxis" : {
            "title": "x-axis",
            "autotick": False
        }
    }
    
    layout = Layout.from_dict(lt)
    print(layout.to_dict())
    
def test_051():
    
    tr = {
        "x": [1.0, 2.0],
        "y": [1.1, 1.2],
        "type": PlotType.SCATTER.value,
        "mode": Mode.LINES_MARKERS.value
    }
    
    trace = Trace.from_dict(tr)
    print(trace.to_dict())
    
def test_052():

    tr = {
        "x": [1.0, 2.0],
        "y": [1.1, 1.2],
        "type": PlotType.SCATTER.value,
        "mode": Mode.LINES_MARKERS.value
    }
    
    d = [tr]
     
    lt = {
        "title": {
            "text": "test title"
        },
        "xaxis" : {
            "title": "x-axis",
            "autotick": False
        }
    }
    
    p = Plotly.from_dict(d, lt)
    pdoc = PlotlyDocument(p)
    pdoc.to_file(os.path.dirname(__file__) + os.sep + "plotly_test_052.html")
    
def test_set_color():
    
    tr = Trace()
    tr.set_mode(Mode.LINES_MARKERS).set_line().set_color(Color.RED)
    
    print(tr.to_dict())
    