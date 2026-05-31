from pydag.agents.Agent import Agent
from pydag.agents.ui.UIService import UIService
from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from pydag.agents.ui.UITaskRunnerPage import UITaskRunnerPage
from pydag.utils.FileUtils import FileUtils

def test_000():
    ag = Agent()
    
    trs = TaskRunnerService(description="Test Task Runner Service, that outlines how the UI can be used to run tasks and display results. This is a example only, to showcase the UI, and is not meant to be a real service.")
    trs.add_task(FileUtils.list_files, ["folder", "pattern"], ["files"])
    trs.add_task(FileUtils.get_file_bytes, ["files"], ["bytes"])
    ag.add_service(trs)
    
    uis = UIService(with_mgmt_ui=False, with_buffer_ui=False)
    uis.add_page(UITaskRunnerPage(uis))
    ag.add_service(uis)
    
    ag.release()