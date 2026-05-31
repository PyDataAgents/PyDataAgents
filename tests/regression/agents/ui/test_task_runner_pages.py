from pydag.agents.Agent import Agent
from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from pydag.agents.ui.UITaskRunnerPage import UITaskRunnerPage
from pydag.utils.FileUtils import FileUtils

def test_000():
    ag = Agent(with_ui=True)
    
    trs = TaskRunnerService(description="Test Task Runner Service, that outlines how the UI can be used to run tasks and display results. This is a example only, to showcase the UI, and is not meant to be a real service.")
    trs.add_task(FileUtils.list_files, ["folder", "pattern"], ["files"])
    trs.add_task(FileUtils.get_file_bytes, ["files"], ["bytes"])
    ag.add_service(trs)
    
    ag.add_ui_page(UITaskRunnerPage(ag))
    
    ag.release()