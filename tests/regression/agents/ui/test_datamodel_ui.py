from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.agents.ui.UIDataModelPage import UIDataModelPage
from pydag.services.datamodel.DataModelService import DataModelService
from tests.unit.services.datamodel.SimpleDataModel import SimpleDataModel


def test_simple_datamodel_ui():
    ag = Agent()
    dms = DataModelService()
    dms.set_model(SimpleDataModel)
    
    ag.add_service(dms)
    
    app = AgentApp(port=8081, with_ui=True, with_api=False, dark_mode=False)
    app.set_agent(ag)
    app.add_ui_page(UIDataModelPage(ag, dms, columns=2))
    app.create()
    app.run()
    