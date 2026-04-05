import matplotlib.pyplot as plt


from pydag.buffers.geometry.BallscrewGothicHelix import BallscrewGothicHelix


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
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, rstride=4, cstride=4, linewidth=0, antialiased=True)
    plt.show()