import os
from pydag.buffers.geometry.BallscrewProfile import BallscrewProfile
from pydag.buffers.geometry.Circle import Circle
from pydag.services.plot.PlotlifyService import PlotlifyService


def test_000():
    
    bg = BallscrewProfile(D_w=6.0, f_r=0.55, s=0.2, nut_or_spindle=False)
    
    x,y = bg.create()
    
    file = os.path.dirname(__file__) + os.sep + "plotly_test_000.html"
    p_doc = PlotlifyService.line(x, y)
    p_doc.get_plotlys()[0].get_layout().get_y_axis().set_scaleanchor("x").set_scaleratio(1)
    
    p_doc.to_file(file)
    
def test_010():
    
    bg1 = BallscrewProfile(D_w=6.0, f_r=0.55, s=0.2, nut_or_spindle=True)
    x1,y1 = bg1.create()
    
    bg2 = BallscrewProfile(D_w=6.0, f_r=0.55, s=0.2, nut_or_spindle=False)
    x2,y2 = bg2.create()
    
    file = os.path.dirname(__file__) + os.sep + "plotly_test_010.html"
    p_doc = PlotlifyService.lines([x1, x2], [y1, y2])
    p_doc.get_plotlys()[0].get_layout().get_y_axis().set_scaleanchor("x").set_scaleratio(1)
    
    p_doc.to_file(file)
    
def test_020():
    
    bg1 = BallscrewProfile(D_w=6.0, f_r=0.55, s=1.0, nut_or_spindle=True)
    x1,y1 = bg1.create()
    
    bg2 = BallscrewProfile(D_w=6.0, f_r=0.55, s=1.0, nut_or_spindle=False)
    x2,y2 = bg2.create()
    
    c = Circle(r=3.0)
    x3, y3 = c.create()
    
    file = os.path.dirname(__file__) + os.sep + "plotly_test_020.html"
    p_doc = PlotlifyService.lines([x1, x2, x3], [y1, y2, y3])
    p_doc.get_plotlys()[0].get_layout().get_y_axis().set_scaleanchor("x").set_scaleratio(1)
    
    p_doc.to_file(file)