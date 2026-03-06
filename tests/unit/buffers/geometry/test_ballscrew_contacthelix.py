import os
import numpy as np

from pydag.buffers.geometry.Helix import Helix
from pydag.buffers.geometry.BallscrewContactHelix import BallscrewContactHelix
from pydag.services.plot.PlotlifyService import PlotlifyService

def test_000():
    
    P = 10.0
    D_pw = 40.5
    D_w = 6.0
    alpha = 45.0
    i = 3.0
    
    h1 = Helix(d=D_pw, P=P, i=i)
    x1, y1, z1 = h1.create(resolution_1=1000)    
    
    h2 = BallscrewContactHelix(D_pw=D_pw, D_w=D_w, P=P, i=i, alpha=alpha, nut_or_spindle=True, left_or_right_flank=True)
    x2, y2, z2 = h2.create(resolution_1=1000)
    
    h3 = BallscrewContactHelix(D_pw=D_pw, D_w=D_w, P=P, i=i, alpha=alpha, nut_or_spindle=True, left_or_right_flank=False)
    x3, y3, z3 = h3.create(resolution_1=1000)
    
    h4 = BallscrewContactHelix(D_pw=D_pw, D_w=D_w, P=P, i=i, alpha=alpha, nut_or_spindle=False, left_or_right_flank=True)
    x4, y4, z4 = h4.create(resolution_1=1000)
    
    h5 = BallscrewContactHelix(D_pw=D_pw, D_w=D_w, P=P, i=i, alpha=alpha, nut_or_spindle=False, left_or_right_flank=False)
    x5, y5, z5 = h5.create(resolution_1=1000)
       
    file_path = os.path.dirname(__file__) + "/test_ballscrew_contact_helix_plot.html"
    pDoc = PlotlifyService.lines([x1, x2, x3, x4, x5], [y1, y2, y3, y4, y5], [z1, z2, z3, z4, z5], names = ["D_pw", "D_fn_1", "D_fn_2", "D_fs_1", "D_fs_2"])
    pDoc.get_plotlys()[0].get_layout().set_height(1200).set_width(1200)
    pDoc.to_file(file_path)
    
    