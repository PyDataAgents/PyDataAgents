from __future__ import annotations
from dataclasses import dataclass, field
import importlib.util
import os
import inspect
from typing import Any, Callable
from functools import wraps


from ..ServiceException import ServiceException
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService


def task(func=None, *, name=None):
    def decorator(f):
        f._is_task = True
        f._task_name = name or f.__name__
        f._signature = inspect.signature(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        # preserve metadata on wrapper too
        wrapper._is_task = True
        wrapper._task_name = f._task_name
        wrapper._signature = f._signature

        return wrapper

    return decorator(func) if func else decorator

class Task:
    def __init__(self, func, parent : Task = None):
        self._func = func
        self._name = getattr(func, "_task_name", func.__name__)
        self._sig = getattr(func, "_signature", inspect.signature(func))
        self._outputs : set[str] = set()
        self._parents : list[Task] = list()
        if parent:
            self._parents.append(parent)

    def run(self, context : dict[str, Any]):
        params = {}
        for param in self._sig.parameters:
            if param in context:
                params[param] = context[param]
        #print(f"Running {self.name} with {params}")
        if len(params) != len(self._sig.parameters):
            parent : Task
            p : int = 0
            for parent in self._parents:
                for out in parent.outputs:
                    params[self._sig.parameters[p]] = context[out]
                    p += 1
                    if p > len(self._sig.parameters):
                        break
                if p > len(self._sig.parameters):
                    break
            if len(self._sig.parameters) != len(params):
                raise ServiceException(f"Parameter Input / Outputs for {self.name()} and {parent.name()} do not match")
        result = self._func(**params)
        if isinstance(result, dict):
            context.update(result)
            self._outputs = result.keys()
        else:
            context[self._name] = result
            self._outputs.add(self._name)
        return context
    
    def parents(self) -> Task:
        return self._parents

    def outputs(self) -> list[str]:
        return self._outputs
    
    def name(self) -> str:
        return self._name

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
    
    task_files : list[str] = field(default_factory=list, metadata={"description": ""})
    task_sequence : list[str] = field(default_factory=list, metadata={"description": ""})
    auto_start : bool = field(default=False, metadata={"description": "specifies whether to start the mapping with agent start"})
    
    def __post_init__(self):
        self._tasks : list[Task] = list()        

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # find all tasks in specified task_files by loading and inspecting code
        
        available_funcs : dict[str, Callable] = dict()
        for file_path in self.task_files:
            module = self._load_module_from_path(file_path)
            for _, obj in inspect.getmembers(module):
                if callable(obj) and getattr(obj, "_is_task", False):
                    available_funcs[obj.__name__] = obj
                    
        for task_str in self.task_sequence:        
            if task_str in available_funcs:
                self.add_task(available_funcs[task_str])
        observer : Observer = TaskObserver(self)
        self._observer_thread.add_observer(observer)

    def run(self, context : dict[str, Any]) -> dict[str, Any]:
        context = context or {}
        for t in self._tasks:
            context = t.run(context)
        return context
    
    def add_task(self, func : Callable) -> Task:
        t : Task = Task(func)
        self._tasks.append(t)
        return t
        
    def _load_module_from_path(self, file_path: str):
        file_path = os.path.abspath(file_path)

        module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)

        if spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        spec.loader.exec_module(module)

        return module