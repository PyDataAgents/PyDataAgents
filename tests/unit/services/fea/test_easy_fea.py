from EasyFEA import Display, ElemType, Models, Simulations
from EasyFEA.Geoms import Domain
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")  # non-GUI backend, comment if you want to see the plots

def test_000():
    # ----------------------------------------------
    # Mesh
    # ----------------------------------------------
    L = 120  # mm
    h = 13

    domain = Domain((0, 0), (L, h), h / 3)
    mesh = domain.Mesh_2D([], ElemType.QUAD9, isOrganised=True)
    Display.Plot_Mesh(mesh)

    # ----------------------------------------------
    # Simulation
    # ----------------------------------------------
    E = 210000  # MPa
    v = 0.3
    F = -800  # N

    mat = Models.Elastic.Isotropic(2, E, v, planeStress=True, thickness=h)

    simu = Simulations.Elastic(mesh, mat)

    nodesX0 = mesh.Nodes_Conditions(lambda x, y, z: x == 0)
    nodesXL = mesh.Nodes_Conditions(lambda x, y, z: x == L)

    simu.add_dirichlet(nodesX0, [0, 0], ["x", "y"])
    simu.add_surfLoad(nodesXL, [F / h / h], ["y"])

    simu.Solve()

    # ----------------------------------------------
    # Results
    # ----------------------------------------------
    Display.Plot_Mesh(simu, deformFactor=10)
    Display.Plot_BoundaryConditions(simu)
    Display.Plot_Result(simu, "uy", plotMesh=True)
    Display.Plot_Result(simu, "Svm", plotMesh=True, ncolors=11)
    
    plt.show()