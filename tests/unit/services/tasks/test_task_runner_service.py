import os

from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from tests.unit.services.tasks.tasktest import hello, goodbye, count

def test_specify_sequence_by_file():
    task_files = [os.path.dirname(__file__) + os.sep + "tasktest.py"]
    task_sequence = ["hello", "goodbye"]
    trs = TaskRunnerService(task_files=task_files, task_sequence=task_sequence)
    trs.install()
    
    data = trs.run({"name": "John"})
    print(data)
    
    assert len(data) == 3, "context length does not fit"
    

def test_specify_sequence_by_file_2():
    task_files = [os.path.dirname(__file__) + os.sep + "tasktest.py"]
    task_sequence = ["hello"]
    trs = TaskRunnerService(task_files=task_files, task_sequence=task_sequence)
    trs.install()
    
    data = trs.run({"name": "John"})
    print(data)
    
    assert len(data) == 2, "context length does not fit"
    
def test_specify_sequence_in_script():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(hello)
    trs.add_task(goodbye)
    trs.install()
    data = trs.run({"name": "John"})
    print(data)
    
    assert len(data) == 3, "context length does not fit"
    
def test_non_matching_param_names():
    trs : TaskRunnerService = TaskRunnerService()
    trs.add_task(hello)
    trs.add_task(goodbye)
    trs.add_task(count)
    trs.install()
    data = trs.run({"name": "John"})
    print(data)
    assert len(data) == 4, "context length does not fit"