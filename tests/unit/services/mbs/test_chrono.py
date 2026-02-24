import pytest

try:
    import pychrono.core as chrono
    import pychrono.fea as fea
    import pychrono.irrlicht as chronoirr  # For visualization
except (ImportError, ModuleNotFoundError) as exc:
    pytest.skip(f"PyChrono tests require pychrono extras: {exc}", allow_module_level=True)

# Chrono initialization
chrono.SetChronoDataPath(chrono.GetChronoDataPath())

# Create system
system = chrono.ChSystemSMC()

# Parameters
beam_length = 1.0     # meters
beam_radius = 0.01    # meters
num_elements = 10     # Beam resolution
density = 7800        # Steel (kg/m^3)
E = 2.1e11            # Young's modulus
G = 8.0e10            # Shear modulus

# Mesh container
mesh = fea.ChMesh()

# Cross-section
section = fea.ChBeamSectionAdvanced()
section.SetDensity(density)
section.SetYoungModulus(E)
section.SetGshearModulus(G)
section.SetAsRectangular(beam_radius*2, beam_radius*2)

# Create nodes and elements
prev_node = None
beam_nodes = []
dx = beam_length / num_elements

for i in range(num_elements + 1):
    node = fea.ChNodeFEAxyzD(chrono.ChVectorD(i * dx, 0, 0),
                             chrono.ChVectorD(0, 1, 0))  # Initial direction
    node.SetMass(0)
    mesh.AddNode(node)
    beam_nodes.append(node)

    if i > 0:
        element = fea.ChElementBeamEuler()
        element.SetNodes(beam_nodes[i - 1], beam_nodes[i])
        element.SetSection(section)
        mesh.AddElement(element)

# Add mesh to system
system.Add(mesh)

# === Bearings (revolute joints at both ends) ===
ground = chrono.ChBody()
ground.SetBodyFixed(True)
system.Add(ground)

# Revolute joint at beam start
rev1 = chrono.ChLinkLockRevolute()
rev1.Initialize(beam_nodes[0], ground, chrono.ChCoordsysD(beam_nodes[0].GetPos()))
system.AddLink(rev1)

# Revolute joint at beam end
rev2 = chrono.ChLinkLockRevolute()
rev2.Initialize(beam_nodes[-1], ground, chrono.ChCoordsysD(beam_nodes[-1].GetPos()))
system.AddLink(rev2)

# === Add motor to induce rotation at one end ===
motor = chrono.ChLinkMotorRotationSpeed()
motor.Initialize(beam_nodes[0], ground, chrono.ChFrameD(beam_nodes[0].GetPos()))
motor_speed = chrono.ChFunction_Const(5.0)  # rad/s constant angular velocity
motor.SetSpeedFunction(motor_speed)
system.AddLink(motor)

# === Visualization ===
application = chronoirr.ChVisualSystemIrrlicht()
application.AttachSystem(system)
application.SetWindowSize(1024, 768)
application.SetWindowTitle("Rotating Flexible Beam (PyChrono)")
application.Initialize()
application.AddTypicalSky()
application.AddTypicalCamera(chrono.ChVectorD(0.5, 0.5, 1.2))
application.AddLightWithShadow(chrono.ChVectorD(-3, 3, 6), chrono.ChVectorD(0, 0, 0), 10, 1, 10, 60)

# Attach beam visualization
for element in mesh.GetElements():
    mvisual = fea.ChElementBeamEulerVisualShape()
    mvisual.SetResolution(1)
    element.AddVisualShapeFEA(mvisual)

application.AssetBindAll()
application.AssetUpdateAll()

# === Simulation Loop ===
time_step = 0.001
while application.Run():
    application.BeginScene()
    application.DrawAll()
    system.DoStepDynamics(time_step)
    application.EndScene()