import os

from pydag.services.datamodel.formula_models import FormulaSet
from pydag.services.datamodel.formula_registries import FormulaRegistry


def test_formula_set_load():
    fp : str = os.path.dirname(__file__) + os.sep + "fugenpressung_zylinderverbund.yaml"
    fs : FormulaSet = FormulaRegistry._load_yaml(fp)
    print(fs)

def test_formula_set_load2():
    fp : str = os.path.dirname(__file__) + os.sep + "models" + os.sep + "metrisches_gewinde_geometrie.yaml"
    fs : FormulaSet = FormulaRegistry._load_yaml(fp)
    print(fs) 

def test_formula_registry():
    fr = FormulaRegistry()
    
    print(len(fr.formula_sets()))
    assert len(fr.formula_sets()) > 0
    