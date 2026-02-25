import math
import os
import pytest

pytest.importorskip("ross")

import ross as rs
from ross.units import Q_
import numpy as np

@pytest.mark.skip("")
def test_000():
    
    steel = rs.Material(name="Steel", rho=7810, E=211e9, G_s=81.2e9)
    # Creating a list of shaft elements
    L = 0.25
    i_d = 0
    o_d = 0.05
    N_elem = 6

    shaft_elements = [
        rs.ShaftElement(
            L=L,
            idl=i_d,
            odl=o_d,
            material=steel,
            shear_effects=True,
            rotary_inertia=True,
            gyroscopic=True,
        )
        for _ in range(N_elem)
    ]
    
    disk = rs.DiskElement(
        n=2,
        m=32.58,
        Ip=0.178,
        Id=0.329,
        tag="Disk"
    )
    
    bearing0 = rs.BearingElement(
        n=0, 
        kxx=[0.5e6, 1.0e6, 2.5e6],
        kyy=[1.5e6, 2.0e6, 3.5e6],
        cxx=[0.5e3, 1.0e3, 1.5e3],
        frequency=[0, 1000, 2000],
    )
    
    bearing1 = rs.BearingElement(
        n=5, 
        kxx=[0.5e6, 1.0e6, 2.5e6],
        kyy=[1.5e6, 2.0e6, 3.5e6],
        cxx=[0.5e3, 1.0e3, 1.5e3],
        frequency=[0, 1000, 2000],
    )
    
    bearings = [bearing0, bearing1]
    
    rotor = rs.Rotor(shaft_elements=shaft_elements, disk_elements=[disk], bearing_elements=bearings)
    f1 = rotor.plot_rotor()
    f1.show()
    
    campbell = rotor.run_campbell(speed_range=np.linspace(0, 1000))
    f2 = campbell.plot()
    f2.show()
        

@pytest.mark.skip("")        
def test_010():
    # 20.63.1800.xxxx
    
    cf53 = rs.Material(name="CF53", rho=7690, E=210e9, Poisson=0.3)
    
    L_s = 1.8
    N_elem = 10
    L = L_s / N_elem
    i_d = 0
    o_d = 0.062
    
    shaft_elements = [
        rs.ShaftElement6DoF(
            L=L,
            idl=i_d,
            odl=o_d,
            material=cf53,
            shear_effects=True,
            rotary_inertia=True,
            gyroscopic=True,
        )
        for _ in range(N_elem)
    ]
    
    fixed_bearing = rs.BearingElement6DoF(
        n=0, 
        kxx=0.5e6,
        kyy=1.5e6,
        kzz=1.6e6,
        cxx=0.5e3
    )
    
    loose_bearing = rs.BearingElement6DoF(
        n=10, 
        kxx=0.5e6,
        kyy=1.5e6,
        kzz=0.0,
        cxx=0.5e3
    )
    
    rotor = rs.Rotor(shaft_elements=shaft_elements, bearing_elements=[fixed_bearing, loose_bearing])
    
    rotor.save(os.path.dirname(__file__) + os.sep + "20_63_1800_cf53.toml")
    
    f1 = rotor.plot_rotor()
    f1.show()
    
    campbell = rotor.run_campbell(speed_range=np.linspace(0, 1000))
    f1 = campbell.plot()
    f1.show()
    
    rpm1 = 100
    rpm2 = 120
    
    #crit_speed = rotor.run_critical_speed(speed_range=(rpm1 / 60.0 / math.pi, rpm2 / 60.0 / math.pi))
    crit_speed = rotor.run_critical_speed(num_modes=2)
    print(np.round(crit_speed.wd("rpm")))

@pytest.mark.skip("")
def test_011():
    # 20.63.1800.xxxx    
    cf53 = rs.Material(name="CF53", rho=7690, E=210e9, Poisson=0.3)
    
    L_s = 1.8
    N_elem = 50
    L = L_s / N_elem
    i_d = 0
    o_d = 0.062
    
    shaft_elements = [
        rs.ShaftElement6DoF(
            L=L,
            idl=i_d,
            odl=o_d,
            material=cf53,
            shear_effects=True,
            rotary_inertia=True,
            gyroscopic=True,
        )
        for _ in range(N_elem)
    ]
    
    fixed_bearing = rs.BearingElement6DoF(
        n=0, 
        kxx=1e12,
        kyy=1e12,
        kzz=1e12,
        cxx=0.5e3
    )
    
    loose_bearing = rs.BearingElement6DoF(
        n=50, 
        kxx=1e12,
        kyy=1e12,
        kzz=0.0,
        cxx=0.5e3
    )
    
    rotor = rs.Rotor(shaft_elements=shaft_elements, bearing_elements=[fixed_bearing, loose_bearing])
    rotor.save(os.path.dirname(__file__) + os.sep + "20_63_1800_cf53_stiff.toml")

@pytest.mark.skip("")    
def test_012():
    # 10.40.650.xxxx    
    cf53 = rs.Material(name="CF53", rho=7690, E=210e9, Poisson=0.3)
    
    L_s = 0.65
    N_elem = 10
    L = L_s / N_elem
    i_d = 0
    o_d = 0.0362574
    
    shaft_elements = [
        rs.ShaftElement6DoF(
            L=L,
            idl=i_d,
            odl=o_d,
            material=cf53,
            shear_effects=True,
            rotary_inertia=True,
            gyroscopic=True,
        )
        for _ in range(N_elem)
    ]
    
    fixed_bearing = rs.BearingElement6DoF(
        n=0, 
        kxx=1e12,
        kyy=1e12,
        kzz=1e12,
        cxx=0.5e3
    )
    
    loose_bearing = rs.BearingElement6DoF(
        n=10, 
        kxx=1e12,
        kyy=1e12,
        kzz=0.0,
        cxx=0.5e3
    )
    
    rotor = rs.Rotor(shaft_elements=shaft_elements, bearing_elements=[fixed_bearing, loose_bearing])
    rotor.save(os.path.dirname(__file__) + os.sep + "10_40_650_cf53_stiff.toml")
    f = rotor.plot_rotor()
    f.show()
    
@pytest.mark.skip("")    
def test_020():
    
    rotor = rs.Rotor.load(os.path.dirname(__file__) + os.sep + "20_63_1800_cf53.toml")
    f = rotor.plot_rotor()
    f.show()
    static = rotor.run_static()
    f = static.plot_free_body_diagram()
    f.show()
    f = static.plot_deformation()
    f.show()

@pytest.mark.skip("")    
def test_021():
    
    rotor = rs.Rotor.load(os.path.dirname(__file__) + os.sep + "20_63_1800_cf53_stiff.toml")
    f = rotor.plot_rotor()
    f.show()
    static = rotor.run_static()
    f = static.plot_deformation()
    f.show()
    
@pytest.mark.skip("")
def test_022():
    
    rotor = rs.Rotor.load(os.path.dirname(__file__) + os.sep + "10_40_650_cf53_stiff.toml")
    f = rotor.plot_rotor()
    f.show()
    static = rotor.run_static()
    f = static.plot_deformation()
    f.show()
    
@pytest.mark.skip("")   
def test_030():
    rotor = rs.Rotor.load(os.path.dirname(__file__) + os.sep + "20_63_1800_cf53.toml")
    rpm = 1776
    speed = rpm / 60 * 2 * math.pi
    modal = rotor.run_modal(speed=speed)
    print(f"Undamped natural frequencies:\n {modal.wn / 2 / math.pi *60}")
    
    for i in range(1, len(modal.shapes)):
        f = modal.plot_mode_3d(mode = i, frequency_units = "rpm")
        f.show()

@pytest.mark.skip("")      
def test_031():
    rotor = rs.Rotor.load(os.path.dirname(__file__) + os.sep + "10_40_650_cf53_Stiff.toml")
    rpm = 10
    speed = rpm / 60 * 2 * math.pi
    modal = rotor.run_modal(speed=speed)
    print(f"Undamped natural frequencies:\n {modal.wn / 2 / math.pi *60}")
    print(f"Damped natural frequencies:\n {modal.wd / 2 / math.pi *60}")
    
    for i in range(1, len(modal.shapes)):
        f = modal.plot_mode_3d(mode = i, frequency_units = "rpm")
        f.show()
