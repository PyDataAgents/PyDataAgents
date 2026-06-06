from dataclasses import dataclass
import os

from tests.unit.services.tasks.tasktest import hello, goodbye, count

from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.services.tasks.TaskRunnerService import TaskRunnerService
from pydag.utils.FileUtils import FileUtils


@dataclass
class DoubleValueAction(BufferNode, Action):
    def _on_execute(self):
        data = self.get_parent_data()
        input_key = self.input_keys[0]
        output_key = self.output_keys[0]

        values = data[input_key]
        self.add_data({output_key: [value * 2 for value in values]})


def format_result(value: int) -> str:
    return f"result={value}"


def test_task_runner_service_for_custom_action():
    runner = TaskRunnerService()

    runner.add_task(DoubleValueAction(), ["value"], ["doubled"])
    runner.add_task(format_result, ["doubled"], ["message"])

    runner.install()

    result = runner.run({"value": 21})

    assert result["value"] == 21
    assert result["doubled"] == [42]
    assert result["message"] == ["result=42"]
    
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