import os


from pydag.buffers.geometry.BallscrewGothicHelix import BallscrewGothicHelix
from pydag.services.plot.PlotlifyService import PlotlifyService
from pydag.services.plot.PlotlyElements import ColorNames


def test_gothicarchhelix():

    helix = BallscrewGothicHelix(
        groove_pitch_diameter=40.0,        
        pitch=10,
        contact_angle_deg=45,
        ball_diameter=6,
        conformity=0.95,
        turns=2
    )

    X, Y, Z = helix.mesh()
    
    pdoc = PlotlifyService.surface(X, Y, Z, color = ColorNames.LIGHT_BLUE.value, name="gothicarchhelix")
    pdoc.to_file(f"{os.path.dirname(__file__)}{os.sep}test_gothicarchhelix.html")