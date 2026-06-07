from pydag.agents.Agent import Agent
from pydag.agents.ui.UIDataModelPage import UIDataModelPage
from pydag.services.datamodel.DataModelService import DataModelService
from tests.unit.services.datamodel.SimpleDataModel import SimpleDataModel


def test_simple_datamodel_ui():
    ag = Agent(port=8080, with_ui=True, with_api=False, dark_mode=False)
    dms = DataModelService()
    dms.set_model(SimpleDataModel)
    
    ag.add_service(dms)
    
    ag.add_ui_page(UIDataModelPage(ag, dms))
    
    ag.release()
    