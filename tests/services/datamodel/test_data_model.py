import os
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.utils.DataUtils import DataUtils


def test_000():
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.getcwd() + os.sep + "tests" + os.sep + "services" + os.sep + "datamodel" + os.sep + "SimpleDataModel.py"
    dms.script_path = os.getcwd() + os.sep + "tests" + os.sep + "services" + os.sep + "datamodel" + os.sep + "SimpleModelScript.py"
    
    dms.install()
    
    dms.data_model.set_data("a", 1.5) 
    
    print(dms.data_model.to_dict())
    print(dms.data_model.to_dict(True))
    
    
def test_010():
    d = {
        "A": [1.0, 2.0, 3.0],
        "B": [10.0, 12.0, 15.0]
    }
    
    df = DataUtils.dict_to_dataframe(d)
    
    df_f = df.query("A < 2.0")
    df_f = df_f["A"]
    print(type(df_f))
    print(df_f)
    print(type(df_f.to_list()[0]))
    print(type(df_f[0]))