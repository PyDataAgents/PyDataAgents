from __future__ import annotations
from dataclasses import dataclass, field
import importlib.util
import os
import inspect
from typing import Any
import typing

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
    description : str = field(default=None, metadata={"description": "description of the task runner service"})
    
    def __post_init__(self):
        super().__post_init__()
        self._funcs : list[callable] = list()
        self._inputs : list[list[type]] = list()
        self._outputs : list[list[type]] = list()        
        self._input_fields : dict[str, type] = dict()
        self._output_fields : dict[str, type] = dict()
        
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
            if len(self.task_sequence) == len(self.inputs) and len(self.task_sequence) == len(self.outputs):
                i : int = 0
                for task_str in self.task_sequence:        
                    if task_str in available_funcs:
                        func = available_funcs[task_str]
                        sig = inspect.signature(func)
                        cp = 0 # compulsory parameters
                        op = 0 # optional parameters
                        for name, param in sig.parameters.items():
                            if param.default is not inspect.Parameter.empty:
                                op += 1
                            else:
                                cp += 1
                        if len(self.inputs[i]) < cp or len(self.inputs[i]) > cp + op:
                            raise ServiceException("number of specified inputs does not match method signature")
                        
                        self.add_task(available_funcs[task_str], self.inputs[i], self.outputs[i])
                    i += 1
        if len(self._funcs) == 0:
            raise ServiceException("no tasks were specified")
        i : int = 0
        for func in self._funcs:
            # get input type hints
            sig = inspect.signature(func)
            cp = 0 # compulsory parameters
            op = 0 # optional parameters
            input_types : list[type] = list()
            for name, param in sig.parameters.items():
                if param.default is not inspect.Parameter.empty:
                    op += 1
                else:
                    cp += 1
                if param.annotation is inspect.Parameter.empty:
                    input_types.append(None)
                else:
                    input_types.append(param.annotation)
            self._inputs.append(input_types)
            if len(self.inputs[i]) < cp or len(self.inputs[i]) > cp + op:
                raise ServiceException("number of specified inputs does not match method signature")
            
            # get output type hints
            hints = typing.get_type_hints(func)
            if "return" in hints:
                self._outputs.append([hints["return"]])
            else:
                self._outputs.append([None])
            
            # go over defined input and output field lists and combine them to create
            # a mapping of remaining required external inputs and remaining expected outputs
            # of the task sequence based on the specified sequence and inputs/outputs for each task        
            input_fields = self.inputs[i]
            if len(input_fields) <= len(input_types):
                for j, input_field in enumerate(input_fields):
                    self._input_fields[input_field] = input_types[j]
            output_fields = self.outputs[i]
            if len(output_fields) == len(self._outputs[i]):
                for j, output_field in enumerate(output_fields):
                    self._output_fields[output_field] = self._outputs[i][j]
            i += 1
        
        # find inputs and outputs to remove from expected input/output fields based on inputs/outputs of previous tasks in the sequence
        input_fields_copy = dict(self._input_fields)
        output_fields_copy = dict(self._output_fields)
        for key, value in output_fields_copy.items():
            if key in self._input_fields:
                del self._input_fields[key]
        for key, value in input_fields_copy.items():
            if key in self._output_fields:
                del self._output_fields[key]
        
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
                # check for list input, where only scalar input is expected
                list_indices : list[int] = list()
                list_counts : list[int] = list()
                a : int = 0
                it = iter(self._inputs[i])
                for arg in args:
                    item = next(it)
                    if isinstance(arg, list):
                        if not isinstance(item, list):
                            list_indices.append(a)
                            list_counts.append(len(arg))
                    a += 1
                if len(list_indices) > 0:
                    if all(c == list_counts[0] for c in list_counts):                        
                        result : tuple = tuple([] for _ in range(len(self.outputs[i])))
                        for j in range(list_counts[0]):
                            sub_args = []
                            a = 0
                            for arg in args:
                                if a in list_indices:
                                    sub_args.append(arg[j])
                                else:
                                    sub_args.append(arg)                                             
                            sub_result = func(*sub_args)
                            if isinstance(sub_result, tuple):
                                k : int = 0
                                for item in sub_result:
                                    result[0].append(item)
                                    k += 1
                            else:
                                result[0].append(sub_result)

                    else:
                        raise ServiceException("number of list elements must be the same if list values are specififed for scalar input")
                else:
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
    
    def get_input_fields(self) -> dict[str, type]:
        return self._input_fields
    
    def get_output_fields(self) -> dict[str, type]:
        return self._output_fields
            
    def _load_module_from_path(self, file_path: str):
        file_path = os.path.abspath(file_path)

        module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)

        if spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        spec.loader.exec_module(module)

        return module