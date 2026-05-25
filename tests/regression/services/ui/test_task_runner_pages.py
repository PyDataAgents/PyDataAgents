from pydag.agents.Agent import Agent
from pydag.services.ui.UIService import UIService
from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from pydag.services.ui.UITaskRunnerPage import UITaskRunnerPage
from pydag.utils.FileUtils import FileUtils

def test_000():
    ag = Agent()
    
    trs = TaskRunnerService(description="Test Task Runner Service")
    trs.add_task(FileUtils.list_files, ["folder", "pattern"], ["files"])
    trs.add_task(FileUtils.get_file_bytes, ["files"], ["bytes"])
    ag.add_service(trs)
    
    uis = UIService(with_mgmt_ui=False, with_buffer_ui=False)
    uis.add_page(UITaskRunnerPage(uis))
    ag.add_service(uis)
    
    ag.release()
    
test_000()