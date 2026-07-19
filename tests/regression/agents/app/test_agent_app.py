import os

from pydag.agents.app.AgentApp import AgentApp
from pydag.agents.ui.UIElements import UIPage
from pydag.agents.ui.UILogPage import UILogPage
from pydag.utils.logs.LogUtils import add_memory_logstore


def test_agent_app():
    file_path = os.path.dirname(__file__) + os.sep + "csv_agent_app_template.yaml"
    aa = AgentApp.load(file_path)
    aa.create()
    aa.run()
    
def test_agent_app_with_log():
    add_memory_logstore()
    file_path = os.path.dirname(__file__) + os.sep + "csv_agent_app_template.yaml"
    aa = AgentApp.load(file_path)
    lp : UIPage = UILogPage(aa.get_agent(), 2)
    aa.add_ui_page(lp)
    aa.create()
    aa.run()