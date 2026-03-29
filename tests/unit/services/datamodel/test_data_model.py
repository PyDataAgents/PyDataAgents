import os
import pytest


from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.datamodel.DataModelService import DataModelService
from pydag.utils.DataUtils import DataUtils
from pydag.agents.Agent import Agent


@pytest.mark.asyncio
async def test_000():
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    dms.install()
    
    session_id = dms.create_session()
    
    await dms.update(session_id, "M1", "a", 1.5)
    
    d1 = dms.get_data_model(session_id, "M1").to_dict()
    assert len(d1) == 3
    d2 = dms.get_data_model(session_id, "M1").to_dict(True)
    assert len(d2) == 5
    
    
@pytest.mark.asyncio
async def test_001():
    
    dms = DataModelService()
    dms.model_name = "SimpleDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"
    
    dms.install()
    
    session_id = dms.create_session()
    await dms.updates(session_id, "M1", {"a": 1.5}) 
    
    d1 = dms.get_data_model(session_id, "M1").to_dict()
    assert len(d1) == 3
    d2 = dms.get_data_model(session_id, "M1").to_dict(True)
    assert len(d2) == 5
   
    
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
    
    
@pytest.mark.asyncio
async def test_model_with_lookup():
    
    a = Agent()
    buf = DictBuffer(id="BUF")
    buf.push(
        {
         "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
         "B": ["A", "AA", "AAA", "B", "BB", "BBB", "C", "CC", "CCC", "Z"]
         }
    )
    a.add_buffer(buf)
    buf.install(a)
    
    dms = DataModelService()
    dms.model_name = "SimpleLookupDataModel"
    dms.model_path = os.path.dirname(__file__) + os.sep + "SimpleLookupDataModel.py"
    dms.install(a)
    
    a.add_service(dms)
    
    session_id = dms.create_session()
    await dms.update(session_id, "M1", "a", 4)
    
    d1 = dms.get_data_model(session_id, "M1").to_dict()
    assert len(d1) == 4
    d2 = dms.get_data_model(session_id, "M1").to_dict(True)
    assert len(d2) == 6