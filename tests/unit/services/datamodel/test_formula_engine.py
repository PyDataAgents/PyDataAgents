import os

import pandas as pd

from pydag.services.datamodel.formula_engine import FormulaEngine
from pydag.services.datamodel.formula_models import FormulaSet, SymbolInput
from pydag.services.datamodel.formula_registries import FormulaRegistry


def test_engine_example1_fugenpressung():
    inputs = {
        "D_F": SymbolInput(unit="mm", value=50.0),
        "D_iI": SymbolInput(unit="mm", value=0.0),    
        "D_aA": SymbolInput(unit="mm", value=100.0),
        "R_zI": SymbolInput(unit="µm", value=6.0),
        "R_zA": SymbolInput(unit="µm", value=6.0),
        "R_el_I": SymbolInput(unit="MPa", value=200.0),
        "R_el_A": SymbolInput(unit="MPa", value=300.0),
        "E_I": SymbolInput(unit="MPa", value=215000.0),
        "E_A": SymbolInput(unit="MPa", value=215000.0),
        "nu_I": SymbolInput(unit="dimensionless", value=0.3),
        "nu_A": SymbolInput(unit="dimensionless", value=0.3),
        "p": SymbolInput(unit="MPa", value=90.0)
    }
    
    fp : str = os.path.dirname(__file__) + os.sep + "fugenpressung.yaml"
    fs : FormulaSet = FormulaRegistry._load_yaml(fp)
    res : dict = FormulaEngine.solve(fs, inputs, {"U_i": "mm"})
    print(res)
    assert res["U_i"]["unit"] == "mm"
    assert round(res["U_i"]["value"], 4) == 0.0654

def test_engine_example2_fugenpressung():
    inputs = {
        "D_F": SymbolInput(unit="mm", value=50.0),
        "D_iI": SymbolInput(unit="mm", value=0.0),    
        "D_aA": SymbolInput(unit="mm", value=100.0),
        "R_zI": SymbolInput(unit="µm", value=6.0),
        "R_zA": SymbolInput(unit="µm", value=6.0),
        "R_el_I": SymbolInput(unit="MPa", value=200.0),
        "R_el_A": SymbolInput(unit="MPa", value=300.0),
        "E_I": SymbolInput(unit="MPa", value=215000.0),
        "E_A": SymbolInput(unit="MPa", value=215000.0),
        "nu_I": SymbolInput(unit="dimensionless", value=0.3),
        "nu_A": SymbolInput(unit="dimensionless", value=0.3),
        "U_i": SymbolInput(unit="µm", value=75.0)
    }
    
    fp : str = os.path.dirname(__file__) + os.sep + "fugenpressung.yaml"
    fs : FormulaSet = FormulaRegistry._load_yaml(fp)
    res : dict = FormulaEngine.solve(fs, inputs, {"U_w": "µm", "p": "MPa"})
    print(res)
    assert res["p"]["unit"] == "MPa"
    assert round(res["p"]["value"], 1) == 105.5
    assert res["U_w"]["unit"] == "µm"
    assert round(res["U_w"]["value"], 1) == 65.4
    
def test_engine_example3_fugenpressung():
    inputs = {
        "D_F": SymbolInput(unit="mm", value=50.0),
        "D_iI": SymbolInput(unit="mm", value=10.0),    
        "D_aA": SymbolInput(unit="mm", value=125.0),
        "R_zI": SymbolInput(unit="µm", value=6.0),
        "R_zA": SymbolInput(unit="µm", value=6.0),
        "R_el_I": SymbolInput(unit="MPa", value=300.0),
        "R_el_A": SymbolInput(unit="MPa", value=150.0),
        "E_I": SymbolInput(unit="MPa", value=215000.0),
        "E_A": SymbolInput(unit="MPa", value=70000.0),
        "nu_I": SymbolInput(unit="dimensionless", value=0.3),
        "nu_A": SymbolInput(unit="dimensionless", value=0.3),
        "p": SymbolInput(unit="MPa", value=50.0)
    }
    
    fp : str = os.path.dirname(__file__) + os.sep + "fugenpressung.yaml"
    fs : FormulaSet = FormulaRegistry._load_yaml(fp)
    res : dict = FormulaEngine.solve(fs, inputs, {"U_i": "µm", "Q_I": "dimensionless"})
    print(res)
    assert res["U_i"]["unit"] == "µm"
    assert round(res["U_i"]["value"], 1) == 78.7
    assert res["Q_I"]["unit"] == "dimensionless"
    assert res["Q_I"]["value"] == 0.2
    
def test_minus_set():
    A = set(["A", "B", "C"])
    B = set(["A", "B"])
    C = A - B
    print(C)
    assert C == set("C")
    
def test_combine_set():
    A = set(["B", "A"])
    B = set(["A", "B", "C", "D"])
    D = set("D")
    C = (A & B) | D
    print(C)
    assert C == set(["A", "B", "D"])
    
def test_df_filter():
    d = {"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]}
    df = pd.DataFrame(d)
    result = df.loc[df["B"]=="b", "A"].values[0]
    print(result)
    
def test_df_filter2():
    d = {"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]}
    df = pd.DataFrame(d)
    result = df.query("A > 1 and B == 'b'")["C"].iloc[0]
    print(result)