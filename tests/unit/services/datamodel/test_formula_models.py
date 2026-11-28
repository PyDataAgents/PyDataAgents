import os

from pydag.services.datamodel.formula_models import Lookup


def test_lookup():
    fp = os.path.dirname(__file__) + os.sep + "metrisches_gewinde_geometrie.xlsx"
    qi = {"D": 4.5}
    lu = Lookup(source="xlsx", endpoint=f"[{fp}]TABLE_METRIC_SCREWS", target="Pitch P [mm]", query="`Major Diameter D [mm]` == @D")
    res = lu.lookup(qi)
    print(res)
    

def test_lookup2():
    fp = os.path.dirname(__file__) + os.sep + "metrisches_gewinde_geometrie.xlsx"
    lu = Lookup(source="xlsx", endpoint=f"[{fp}]TABLE_METRIC_SCREWS", target="Pitch P [mm]", query="`Major Diameter D [mm]` == @D and `Pitch P [mm]` >= @P")
    p = lu.get_query_params()
    print(p)
    assert p == {"D", "P"}