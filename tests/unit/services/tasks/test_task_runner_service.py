import os

from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from pydag.utils.FileUtils import FileUtils
from tests.unit.services.tasks.tasktest import hello, goodbye, count

def test_specify_sequence_by_file():
    task_files = [os.path.dirname(__file__) + os.sep + "tasktest.py"]
    task_sequence = ["hello", "goodbye"]
    inputs = [["name"], ["name"]]
    outputs = [["greeting"], ["farewell"]]
    trs = TaskRunnerService(task_files=task_files, task_sequence=task_sequence, inputs=inputs, outputs=outputs)
    trs.install()
    data = trs.run({"name": "John"})
    print(data)    
    assert len(data) == 3, "context length does not fit"

def test_specify_sequence_by_file_2():
    task_files = [os.path.dirname(__file__) + os.sep + "tasktest.py"]
    task_sequence = ["hello"]
    inputs = [["name"]]
    outputs = [["greeting"]]
    trs = TaskRunnerService(task_files=task_files, task_sequence=task_sequence, inputs=inputs, outputs=outputs)
    trs.install()    
    data = trs.run({"name": "John"})
    print(data)    
    assert len(data) == 2, "context length does not fit"
    
def test_specify_sequence_in_script():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(hello, ["name"], ["greeting"])
    trs.add_task(goodbye, ["name"], ["farewell"])
    trs.install()
    data = trs.run({"name": "John"})
    print(data)    
    assert len(data) == 3, "context length does not fit"
    
def test_specify_sequence_in_script2():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(hello, ["name"], ["greeting"])
    trs.add_task(goodbye, ["name"], ["farewell"])
    trs.add_task(count, ["farewell"], ["count"])
    trs.install()
    data = trs.run({"name": "John"})
    print(data)
    assert len(data) == 4, "context length does not fit"
    
def test_static_func():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(FileUtils.list_files, ["folder", "pattern"], ["files"])
    trs.install()
    folder = os.path.dirname(__file__)
    data = trs.run({"folder": folder, "pattern": "py"})
    print(data)
    
def test_static_func2():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(FileUtils.list_files, ["folder", "pattern"], ["files"])
    trs.add_task(FileUtils.get_file_bytes, ["files"], ["bytes"])
    trs.install()
    folder = os.path.dirname(__file__)
    data = trs.run({"folder": folder, "pattern": "py"})
    print(data)