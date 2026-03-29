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
    
    m_id = mms.create_model(s_id, "SimpleDataModel")
    
    await mms.update(s_id, m_id, "a", 1.5)
    
    d1 = mms.get_data_model(s_id, m_id).to_dict()
    assert len(d1) == 3
    d2 = mms.get_data_model(s_id, m_id).to_dict(True)
    assert len(d2) == 5
    