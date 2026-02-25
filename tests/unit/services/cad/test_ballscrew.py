import math

import pytest

cq = pytest.importorskip("cadquery")


def test_000():
    L_n = 89
    D_1 = 42
    L_7 = 14
    D_6 = 93
    D_z = 63
    L_1 = 16
    D_n_a = 62.8
    L_AbstreiferTiefe = 10
    D_AbstreiferFreidrehung = 52.1
    D_2_f = 46.9


    base_sketch = (
        cq.Workplane("XY")
        .lineTo(0, D_AbstreiferFreidrehung / 2, forConstruction=True)
        .lineTo(0, D_6 / 2)
        .lineTo(L_7, D_6 / 2)
        .lineTo(L_7, D_z / 2)
        .lineTo(L_7 + L_1, D_z / 2)
        .lineTo(L_7 + L_1 + (D_z - D_n_a) / 2 / math.tan(30/180*math.pi), D_n_a / 2)
        .lineTo(L_n, D_n_a / 2)
        .lineTo(L_n, D_AbstreiferFreidrehung / 2)
        .lineTo(L_n - L_AbstreiferTiefe, D_AbstreiferFreidrehung /2)
        .lineTo(L_n - L_AbstreiferTiefe, D_2_f / 2)
        .lineTo(L_n - L_AbstreiferTiefe - (D_2_f - D_1) / 2 * math.tan(30/180*math.pi), D_1 / 2)
        .lineTo(L_AbstreiferTiefe + (D_2_f - D_1) / 2 * math.tan(30/180*math.pi), D_1 / 2)
        .lineTo(L_AbstreiferTiefe, D_2_f / 2)
        .lineTo(L_AbstreiferTiefe, D_AbstreiferFreidrehung / 2)
        .close()
    )

    base_solid = base_sketch.revolve(angleDegrees = 360, axisStart=(0, 0), axisEnd=(L_n, 0))

    #show_object(solid)
