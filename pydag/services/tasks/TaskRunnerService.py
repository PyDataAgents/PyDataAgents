from __future__ import annotations
from dataclasses import dataclass, field
import importlib.util
import os
import inspect
from typing import Any

from ..ServiceException import ServiceException
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService

class TaskObserver(Observer):

    def __init__(self, service: TaskRunnerService):
        super().__init__()
        self._service : TaskRunnerService = service

    def observe(self):
        self._service.run({})

    def unobserve(self):
        return

@dataclass
class TaskRunnerService(ObserverService):
    """ A `Service` for running tasks chained together as methods with specified inputs """
    
    task_files : list[str] = field(default_factory=list, metadata={"description": ""})
    task_sequence : list[str] = field(default_factory=list, metadata={"description": ""})
    inputs : list[list[str]] = field(default_factory=list, metadata={})
    outputs : list[list[str]] = field(default_factory=list, metadata={})
    auto_start : bool = field(default=False, metadata={"description": "specifies whether to start the mapping with agent start"})
    
    def __post_init__(self):
        super().__post_init__()
        self._funcs : list[callable] = list()
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # find all tasks in specified task_files by loading and inspecting code
        if len(self.task_files) > 0:
            available_funcs : dict[str, callable] = dict()
            for file_path in self.task_files:
                module = self._load_module_from_path(file_path)
                for _, obj in inspect.getmembers(module):
                    if callable(obj):
                        available_funcs[obj.__name__] = obj
            i : int = 0
            if len(self.task_sequence) == len(self.inputs) and len(self.task_sequence) == len(self.outputs):
                for task_str in self.task_sequence:        
                    if task_str in available_funcs:
                        func = available_funcs[task_str]
                        sig = inspect.signature(func)
                        ip : int = len(sig.parameters)
                        if ip != len(self.inputs[i]):
                            raise ServiceException("number of specified inputs does not match method signature")
                        
                        self.add_task(available_funcs[task_str], self.inputs[i], self.outputs[i])
                    i += 1
        observer : Observer = TaskObserver(self)
        self.add_observer(observer)

    def run(self, context : dict[str, Any]) -> dict[str, Any]:
        """ run all the tasks """
        new_context = context or {}
        i : int = 0
        for func in self._funcs:
            input_keys = self.inputs[i]
            if len(input_keys) > 0:
                args = [new_context[k] for k in input_keys]
                result = func(*args)
            else:
                result = func()
            output_keys = self.outputs[i]
            data = {}
            if isinstance(result, tuple):
                j : int = 0
                for item in result:
                    data[output_keys[j]] = item
                    j += 1
            else:
                data[output_keys[0]] = result           
            new_context.update(data)
            i += 1
        return new_context
    
    def add_task(self, func : callable, input_keys : list[str], output_keys : list[str]):
        self._funcs.append(func)
        self.inputs.append(input_keys)
        self.outputs.append(output_keys)
            
    def _load_module_from_path(self, file_path: str):
        file_path = os.path.abspath(file_path)

        module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)

        if spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        spec.loader.exec_module(module)

        return module