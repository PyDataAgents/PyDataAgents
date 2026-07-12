import os
import pytest


from pydag.services.datamodel.MultiModelService import MultiModelService


@pytest.mark.asyncio
async def test_multi_model_with_1model():
    model_names = ["SimpleDataModel"]
    model_paths = [os.path.dirname(__file__) + os.sep + "SimpleDataModel.py"]
    mms = MultiModelService(model_names=model_names, model_paths=model_paths)
    mms.install()
    
    s_id = mms.create_session()    
    
    m_id = mms.create_model(s_id, "SimpleDataModel.SimpleDataModel")
    
    await mms.updates(s_id, m_id, {"a": 1.5})
    
    d1 = mms.get_data_model(s_id, m_id).to_dict()
    assert len(d1) == 6
    d2 = mms.get_data_model(s_id, m_id).to_dict(True)
    assert len(d2) == 7
    

@pytest.mark.asyncio
async def test_multi_model_with_2models():
    model_names = ["SimpleDataModel", "AnotherSimpleDataModel"]
    model_paths = [os.path.dirname(__file__) + os.sep + "SimpleDataModel.py", os.path.dirname(__file__) + os.sep + "AnotherSimpleDataModel.py"]
    mms = MultiModelService(model_names=model_names, model_paths=model_paths)
    mms.install()
    
    s_id = mms.create_session()    
    
    m1_id = mms.create_model(s_id, "SimpleDataModel.SimpleDataModel")
    
    await mms.updates(s_id, m1_id, {"a": 1.5})
    
    d1 = mms.get_data_model(s_id, m1_id).to_dict()
    assert len(d1) == 6
    d2 = mms.get_data_model(s_id, m1_id).to_dict(True)
    assert len(d2) == 7
    
    m2_id = mms.create_model(s_id, "AnotherSimpleDataModel.AnotherSimpleDataModel")
    
    await mms.updates(s_id, m2_id, {"x": 1.5})
    
    d1 = mms.get_data_model(s_id, m2_id).to_dict()
    assert len(d1) == 4
    
    
@pytest.mark.asyncio
async def test_multi_model_sessions():
    model_names = ["SimpleDataModel", "AnotherSimpleDataModel"]
    model_paths = [os.path.dirname(__file__) + os.sep + "SimpleDataModel.py", os.path.dirname(__file__) + os.sep + "AnotherSimpleDataModel.py"]
    mms = MultiModelService(model_names=model_names, model_paths=model_paths)
    mms.install()
    
    s1_id = mms.create_session()        
    m1_id = mms.create_model(s1_id, "SimpleDataModel.SimpleDataModel")    
    m2_id = mms.create_model(s1_id, "AnotherSimpleDataModel.AnotherSimpleDataModel")
    
    assert len(mms.get_data_models(s1_id)) == 2
    
    
@pytest.mark.asyncio
async def test_multi_model_sessions2():
    model_names = ["SimpleDataModel", "AnotherSimpleDataModel"]
    model_paths = [os.path.dirname(__file__) + os.sep + "SimpleDataModel.py", os.path.dirname(__file__) + os.sep + "AnotherSimpleDataModel.py"]
    mms = MultiModelService(model_names=model_names, model_paths=model_paths)
    mms.install()
    
    s1_id = mms.create_session()        
    m1_id = mms.create_model(s1_id, "SimpleDataModel.SimpleDataModel")    
    m2_id = mms.create_model(s1_id, "AnotherSimpleDataModel.AnotherSimpleDataModel")
           
    m3_id = mms.create_model(s1_id, "SimpleDataModel.SimpleDataModel")
    
    assert len(mms.get_data_models(s1_id)) == 3
    
    s2_id = mms.create_session()
    m1_id = mms.create_model(s2_id, "SimpleDataModel.SimpleDataModel")
    assert len(mms.get_data_models(s2_id)) == 1
    