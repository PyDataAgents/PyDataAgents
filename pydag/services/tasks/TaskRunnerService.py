from __future__ import annotations

from dataclasses import dataclass, field
import importlib.util
import inspect
import os
from typing import Any, Callable
import typing


from ..ThreadType import ThreadType
from ..ServiceException import ServiceException
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService
from ...buffers.DictBuffer import DictBuffer
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode
from ...nodes.buffers.LinkBufferAction import LinkBufferAction


class TaskObserver(Observer):

    def __init__(self, service: TaskRunnerService):
        super().__init__()
        self._service: TaskRunnerService = service

    def observe(self):
        self._service.run({})

    def unobserve(self):
        return

@dataclass
class TaskRunnerService(ObserverService):
    """ A Service for running conventional callables and Action/BufferNode steps in one sequence."""

    task_files: list[str] = field(default_factory=list, metadata={"description": ""})
    task_sequence: list[str] = field(default_factory=list, metadata={"description": ""})
    inputs: list[list[str]] = field(default_factory=list, metadata={})
    outputs: list[list[str]] = field(default_factory=list, metadata={})
    auto_start: bool = field(default=False, metadata={"description": "specifies whether to start the mapping with agent start"})
    thread_type : str = field(default=ThreadType.TRIGGERED.value, metadata={"description": "type of thread to use for running tasks"})
    description: str = field(default=None, metadata={"description": "description of the task runner service"})

    def __post_init__(self):
        super().__post_init__()
        self._tasks: list[dict[str, Any]] = []
        self._input_types: list[list[type | None]] = []
        self._output_types: list[list[type | None]] = []
        self._input_fields: dict[str, type | None] = {}
        self._output_fields: dict[str, type | None] = {}

    def _on_install(self, agent: Agent = None):
        super()._on_install(agent)

        if len(self.task_files) > 0:
            available_funcs: dict[str, callable] = {}
            for file_path in self.task_files:
                module = self._load_module_from_path(file_path)
                for _, obj in inspect.getmembers(module):
                    if callable(obj):
                        available_funcs[obj.__name__] = obj

            if len(self.task_sequence) != len(self.inputs) or len(self.task_sequence) != len(self.outputs):
                raise ServiceException("task_sequence, inputs and outputs must have the same length")

            for i, task_str in enumerate(self.task_sequence):
                if task_str not in available_funcs:
                    raise ServiceException(f"task '{task_str}' was not found in task_files")
                self.add_task(available_funcs[task_str], self.inputs[i], self.outputs[i])

        if len(self._tasks) == 0:
            raise ServiceException("no tasks or nodes were specified")

        self._rebuild_io_schema()
        self.add_observer(TaskObserver(self))

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        new_context = context or {}
        for index, task in enumerate(self._tasks):
            if isinstance(task, Callable):
                data = self._run_callable(task, index, new_context)
            elif isinstance(task, Action):
                data = self._run_action(task, index, new_context)
            else:
                raise ServiceException(f"unknown task runner step kind '{type(task).__name__}'")

            new_context.update(data)

        return new_context

    def add_task(self, task : callable | Action, input_keys: list[str], output_keys: list[str]):
        self._tasks.append(task)
        self.inputs.append(input_keys)
        self.outputs.append(output_keys)

    def get_input_fields(self) -> dict[str, type | None]:
        return self._input_fields

    def get_output_fields(self) -> dict[str, type | None]:
        return self._output_fields

    def _run_callable(self, func : callable, index : int, context : dict[str, Any]) -> dict[str, Any]:
        input_keys = self.inputs[index]
        output_keys = self.outputs[index]

        if len(input_keys) > 0:
            args = [context[k] for k in input_keys]
            result = self._execute_callable_with_list(func, args, self._input_types[index], output_keys)
        else:
            result = func()

        return self._result_to_context(result, output_keys)

    def _run_action(self, action : Action, index : int, context: dict[str, Any]) -> dict[str, Any]:
        input_keys = self.inputs[index]
        output_keys = self.outputs[index]

        if not isinstance(action, BufferNode):
            raise ServiceException("action steps must be BufferNode actions to exchange task context data")

        input_data = {key: context[key] for key in input_keys}
        input_buffer = DictBuffer(timestamps_enabled=False, index_enabled=False)
        output_buffer = DictBuffer(timestamps_enabled=False, index_enabled=False)
        parent = LinkBufferAction()
        parent.set_buffer(input_buffer)
        
        parent.install()
        input_buffer.install()
        output_buffer.install()
        
        action.input_keys = input_keys
        action.output_keys = output_keys
        action.set_buffer(output_buffer)
        if not action.has_parent(parent.id):
            action.add_parent(parent)
        action.install()
        
        input_buffer.push(input_data)
        action.execute()

        data = action.get_buffer().data()
        return {key: data[key] for key in output_keys if key in data}

    def _execute_callable_with_list(self, func: callable, args: list[Any], input_types: list[type | None], output_keys: list[str]) -> Any:
        list_indices: list[int] = []
        list_counts: list[int] = []

        for i, arg in enumerate(args):
            expected_type = input_types[i] if i < len(input_types) else None
            if isinstance(arg, list) and expected_type is not list:
                list_indices.append(i)
                list_counts.append(len(arg))

        if len(list_indices) == 0:
            return func(*args)

        if not all(count == list_counts[0] for count in list_counts):
            raise ServiceException("number of list elements must be the same if list values are specified for scalar input")

        collected = tuple([] for _ in range(len(output_keys)))
        for row_index in range(list_counts[0]):
            sub_args = [
                arg[row_index] if i in list_indices else arg
                for i, arg in enumerate(args)
            ]
            sub_result = func(*sub_args)

            if isinstance(sub_result, tuple):
                for j, item in enumerate(sub_result):
                    collected[j].append(item)
            else:
                collected[0].append(sub_result)

        return collected

    def _result_to_context(self, result: Any, output_keys: list[str]) -> dict[str, Any]:
        if isinstance(result, tuple):
            return {output_keys[i]: item for i, item in enumerate(result)}
        return {output_keys[0]: result}

    def _rebuild_io_schema(self):
        self._input_types.clear()
        self._output_types.clear()
        self._input_fields.clear()
        self._output_fields.clear()
        for i, task in enumerate(self._tasks):
            inputs : list[str] = self.inputs[i]
            outputs : list[str] = self.outputs[i]
            if isinstance(task, Callable):
                input_types, output_types = self._inspect_callable_io(task, inputs, outputs)
            else:
                input_types = [None for _ in inputs]
                output_types = [None for _ in outputs]

            self._input_types.append(input_types)
            self._output_types.append(output_types)

            for i, input_field in enumerate(inputs):
                self._input_fields[input_field] = input_types[i] if i < len(input_types) else None

            for i, output_field in enumerate(outputs):
                self._output_fields[output_field] = output_types[i] if i < len(output_types) else None

        for key in list(self._output_fields.keys()):
            if key in self._input_fields:
                del self._input_fields[key]

        for key in list(self._input_fields.keys()):
            if key in self._output_fields:
                del self._output_fields[key]

    def _inspect_callable_io(self, func: callable, input_keys: list[str], output_keys: list[str]) -> tuple[list[type | None], list[type | None]]:
        sig = inspect.signature(func)
        compulsory = 0
        optional = 0
        input_types: list[type | None] = []

        for _, param in sig.parameters.items():
            if param.default is inspect.Parameter.empty:
                compulsory += 1
            else:
                optional += 1

            if param.annotation is inspect.Parameter.empty:
                input_types.append(None)
            else:
                input_types.append(param.annotation)

        if len(input_keys) < compulsory or len(input_keys) > compulsory + optional:
            raise ServiceException("number of specified inputs does not match method signature")

        hints = typing.get_type_hints(func)
        output_types = [hints["return"]] if "return" in hints else [None]

        if len(output_keys) != len(output_types):
            if len(output_keys) != 1:
                raise ServiceException("number of specified outputs does not match method return values")

        return input_types, output_types

    def _load_module_from_path(self, file_path: str):
        file_path = os.path.abspath(file_path)
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)

        if spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        spec.loader.exec_module(module)
        return module