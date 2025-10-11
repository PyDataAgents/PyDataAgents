import cadquery as cq
import math

""" 
Spindelkonstruktion
"""

L_s = 1000
L_ges = 1200
d_1 = 39
d_zapfen_k1 = 30
L_zapfen_k1 = 50
d_zapfen_l1 = 32
L_zapfen_l1 = 150

spindle_sketch = (
    cq.Workplane("XY")
    .lineTo(0, d_zapfen_k1 / 2)
    .lineTo(L_zapfen_k1, d_zapfen_k1 / 2)
    .lineTo(L_zapfen_k1, d_1 / 2)
    .lineTo(L_zapfen_k1 + L_s, d_1 / 2)
    .lineTo(L_zapfen_k1 + L_s, d_zapfen_l1 / 2)
    .lineTo(L_ges, d_zapfen_l1 / 2)
    .lineTo(L_ges, 0)
    .close()
)

spindle_solid = spindle_sketch.revolve(angleDegrees = 360, axisStart=(0, 0), axisEnd=(L_ges, 0))

#show_object(spindle_solid)

"""
Mutterkonstruktion
"""
L_n = 89
D_1 = 42
L_7 = 14
D_6 = 93
D_z = 63
L_1 = 16
L_3 = 10
D_3 = 62.5
D_n_a = 62.8
L_AbstreiferTiefe = 10
D_AbstreiferFreidrehung = 52.1
D_2_f = 46.9
L_8 = 70
FlanschForm = 'B'
D_4 = 78
D_5 = 9
w_4 = 45
i_Bohrung = 8


# Basis Skizze zum Rotieren erstellen
if L_3 == 0:
    nut_sketch = (
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
else:
    nut_sketch = (
        cq.Workplane("XY")
        .lineTo(0, D_AbstreiferFreidrehung / 2, forConstruction=True)
        .lineTo(0, D_3 / 2)
        .lineTo(L_3, D_3 / 2)
        .lineTo(L_3, D_6 / 2)
        .lineTo(L_3 + L_7, D_6 / 2)
        .lineTo(L_3 + L_7, D_z / 2)
        .lineTo(L_3 + L_7 + L_1, D_z / 2)
        .lineTo(L_3 + L_7 + L_1 + (D_z - D_n_a) / 2 / math.tan(30/180*math.pi), D_n_a / 2)
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

nut_solid = nut_sketch.revolve(angleDegrees = 360, axisStart=(0, 0), axisEnd=(L_n, 0))


# Flanschskizze und Bohrungen erstellen
pts1 = [(L_8 / 2, D_6 / 2)]
match FlanschForm:
    case 'B':
        # beidseitige Flanschabflachung
        flange_cut_out = (
            cq.Workplane("YZ").pushPoints(pts1)
            .rect(D_6 - L_8, -D_6, centered = False)
            .mirrorY()
            .extrude(L_3 + L_7)
        )        
        nut_solid = nut_solid.cut(flange_cut_out)
        nut_solid = (
            nut_solid.faces("<X").workplane()
            .polarArray(radius = D_4 / 2, startAngle = w_4, angle = 2 * w_4, count = int(i_Bohrung / 2))
            .hole(D_5)
        )
        nut_solid = (
            nut_solid.faces("<X").workplane()
            .polarArray(radius = D_4 / 2, startAngle = -w_4, angle = -2 * w_4, count = int(i_Bohrung / 2))
            .hole(D_5)
        )
    case 'C':
        # einseitige Flanschabflachung
        flange_cut_out = (
            cq.Workplane("YZ").pushPoints(pts1)
            .rect(D_6 - L_8, -D_6, centered = False)
            .extrude(L_3 + L_7)
        )
        nut_solid = nut_solid.cut(flange_cut_out)
        nut_solid = (
            nut_solid.faces("<X").workplane()
            .polarArray(radius = D_4 / 2, startAngle = w_4, angle = 2 * w_4, count = int(i_Bohrung / 2))
            .hole(D_5)
        )
        nut_solid = (
            nut_solid.faces("<X").workplane()
            .polarArray(radius = D_4 / 2, startAngle = -w_4, angle = -2 * w_4, count = int(i_Bohrung / 2))
            .hole(D_5)
        )
    case 'A':
        # Rundflansch
        nut_solid = (
            nut_solid.faces("<X").workplane()
            .polarArray(radius = D_4 / 2, startAngle = 0, angle = 360, count = int(i_Bohrung))
            .hole(D_5)
        )

# überall Fasen machen
#nut_solid = nut_solid.edges(">Z").chamfer(0.5)
#nut_solid = nut_solid.edges("<Z").chamfer(0.5)
#nut_solid = nut_solid.edges(">Y").chamfer(0.5)
#nut_solid = nut_solid.edges("<Y").chamfer(0.5)
#nut_solid = nut_solid.edges(">X").chamfer(0.5)
#nut_solid = nut_solid.edges("<X").chamfer(0.5)

# Freistich F
f = 2.5
g = 2.1
t_1 = 0.3
t_2 = 0.2
r = 0.8
w_1 = 8
w_2 = 15
undercut_sketch = (
    cq.Workplane("XY")
    .lineTo(L_7 + f,D_z / 2,forConstruction=True)
)

#show_object(nut_solid)

"""
Abstreiferkonstruktion
"""
L_Abstreifer = 15
D_Abstreifer = 52
d_1 = 39

wiper_sketch = (
    cq.Workplane("XY")
    .lineTo(L_AbstreiferTiefe, d_1 / 2, forConstruction = True)
    .lineTo(L_AbstreiferTiefe, D_Abstreifer / 2)
    .lineTo(L_AbstreiferTiefe - L_Abstreifer, D_Abstreifer / 2)
    .lineTo(L_AbstreiferTiefe - L_Abstreifer, d_1 / 2)
    .close()
)

wiper_solid = wiper_sketch.revolve(angleDegrees = 360, axisStart=(0, 0), axisEnd=(L_n, 0))

#show_object(wiper_solid, options={"color": "lightgray"})


"""
KGT Baugruppe
"""
# Create assembly
asm = (
       cq.Assembly()
       .add(spindle_solid, name="spindle", color = cq.Color("gray"))
       .add(nut_solid, name="nut", color = cq.Color("slategray"), loc = cq.Location(cq.Vector(L_ges / 2, 0, 0)))
       .add(wiper_solid, name="wiper", color = cq.Color("blue"), loc = cq.Location(cq.Vector(L_ges / 2, 0, 0)))
       .add(wiper_solid, name="wiper2", color = cq.Color("blue"), loc = cq.Location(cq.Vector(L_ges / 2 + L_n + L_AbstreiferTiefe - L_Abstreifer, 0, 0)))
)

# constraints
#asm.constrain("nut@faces@<X", "wiper?X", "Plane")

#asm.solve()
show_object(asm)

# export as step
asm.export("out.stp", "STEP", mode="fused")
