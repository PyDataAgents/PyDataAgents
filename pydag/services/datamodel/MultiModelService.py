from __future__ import annotations
import ast
import inspect
from pathlib import Path
from dataclasses import dataclass, field
import threading
from typing import Any
import uuid
from loguru import logger
import pandas as pd
import asyncio


from ..Service import Service
from .DataModelService import DataModelReadAccessVisitor, DataModelSession, DataModelWriteAccessVisitor
from ...buffers.Buffer import Buffer
from ...utils.ClassUtils import ClassUtils
from ..ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ...agents.Agent import Agent
from .DataModel import DataModel


class ModelHandler():
        
    def __init__(self, model_path : str, model_name : str):
        self._model_path : str = model_path
        self._model_name : str = model_name
        self._methods : dict = None
        self._method_input_vars : dict[str, list[str]] = None
        self._method_output_vars : dict[str, list[str]] = None
        self._method_arguments : dict[str, int] = {}
        if self._model_path and self._model_name:        
            if not FileUtils.exists_file(model_path):
                raise ServiceException(f"No model file was found for '{self._model_path}'")        
            self._model_class : type = ClassUtils.load_class(self._model_path, self._model_name)
            self._find_methods()
            self._find_method_vars()
        else:
            raise ServiceException("No model_path or model_name was specified")
    
    def get_model_class(self) -> str:
        return str(self._model_class)
    
    def get_model_path(self) -> str:
        return self._model_path
         
    def _find_methods(self):
        self._methods = ClassUtils.load_methods(self._model_path)
        for name, method in self._methods.items():
            sig = inspect.signature(method)
            params = sig.parameters
            num_args = len([
                p for p in params.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default == p.empty
            ])
            self._method_arguments[name] = num_args
    
    def _find_method_vars(self):
        script_path = Path(self._model_path).resolve()
        source_code = script_path.read_text(encoding="utf-8")
        # Parse file into AST
        tree = ast.parse(source_code)
        visitor1 = DataModelReadAccessVisitor()
        visitor1.visit(tree)
        read_vars : dict = visitor1.read_accesses
        visitor2 = DataModelWriteAccessVisitor()
        visitor2.visit(tree)
        write_vars : dict = visitor2.write_accesses
        all_vars = set()
        for key, wv in write_vars.items():
            all_vars.update(wv)
            if key in read_vars:
                rv : list = read_vars[key]                
                all_vars.update(rv)
                for v in wv:
                    if v in rv:
                        rv.remove(v)
                read_vars[key] = rv
        self._method_input_vars = read_vars
        self._method_output_vars = write_vars
        # validate if method properties exist in model properties
        data_model = ClassUtils.load_instance(self._model_path, self._model_name)
        self._validate_properties(data_model, all_vars)
        
    def _validate_properties(self, data_model : DataModel, properties : set):
        for prop in properties:
            if not data_model.has_property(prop):
                raise ServiceException(f"the script calls a property '{prop}', that does not exist in the model")
            
    def run_methods(self, data_model : DataModel, blocked_vars : str = None) -> int:
        """ runs all methods once and returns how many were executed based on data model values availability
        """
        m : int = 0
        for name, method in self._methods.items():
            input_vars = self._method_input_vars[name]
            method_ready : bool = True
            # check if method is ready based on set inputs
            for input_var in input_vars:
                if not data_model.has_value(input_var):
                    method_ready = False
                    break
            if method_ready:
                # check if the method has output variables that are blocked
                for blocked_var in blocked_vars:
                    if not blocked_var in self._method_output_vars[name]:
                        # check whether to pass only model or lookup as well
                        if self._method_arguments[name] > 1:
                            method(data_model, self)
                        else:                 
                            method(data_model)
                        m = m + 1
        return m
            
@dataclass
class MultiModelService(Service):
    """ `Service` that allows the management of multiple `Datamodel`s at once, enhancing the `DataModelService` capabilities
    """
    
    model_paths : list[str] = field(default=None, metadata={"description": "paths of the model.py files"})
    model_names : list[str] = field(default=None, metadata={"description": "name of the classes to load from the model.py file"})
        
    def __post_init__(self):
        super().__post_init__()
        self._sessions : dict[str, DataModelSession] = dict()
        self._session_locks : dict[str, threading.Lock] = dict()
        self._handlers : dict[str, ModelHandler] = dict()
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if len(self.model_paths) != len(self.model_names):
            raise ServiceException(f"model_paths ({len(self.model_paths)}) and model_names ({len(self.model_names)}) must be of same size")
        i : int = 0
        for model_path in self.model_paths:
            model_name = self.model_names[i]
            self.create_handler(model_path, model_name)
            i += 1
        
    def _on_start(self):
        return

    def _on_stop(self):
        return

    def create_handler(self, model_path : str, model_name : str) -> str:
        handler : ModelHandler = ModelHandler(model_path, model_name)
        handler_id : str = str(handler.get_model_class())
        self._handlers[handler_id] = handler
        return handler_id

    def create_session(self) -> str:
        session_id : str = uuid.uuid4()
        self._sessions[session_id] = DataModelSession()
        self._session_locks[session_id] = asyncio.Lock()
        return session_id
    
    async def create_model(self, session_id : str, model_class : str) -> str:
        lock = self._session_locks[session_id]
        async with lock:
            if model_class in self._handlers:
                session : DataModelSession = self._sessions[session_id]
                model = self._handlers[model_class]()
                model_id = session.add_model(model)
                return model_id
            else:
                raise ServiceException(f"The specified model_class {model_class} is not among registered ModelHandlers")
    
    async def updates(self, session_id : str, model_id : str, property_value_pairs : dict):
        """
        runs all methods over and over again until there is no more updates based on current available model values
        for the given `property_value_pairs`
        """
        lock = self._session_locks[session_id]
        
        async with lock:
            session : DataModelSession = self._sessions[session_id]
            model : DataModel = session.get_model(model_id)
            if model:
                model_class : str = str(model.__class__)
                if model_class in self._handlers:
                    handler : ModelHandler = self._handlers[model_class]         
                    model.set_properties(property_value_pairs)
                    last_success_methods = 0
                    success_methods = handler.run_methods(model, list(property_value_pairs.keys()))
                    # run as long as the number of methods being run successful increases or all methods were run
                    while success_methods > last_success_methods and success_methods is not len(self._methods):
                        last_success_methods = success_methods
                        success_methods = handler.run_methods(model, list(property_value_pairs.keys()))

    async def update(self, session_id : str, model_id : str, property_name : str, value : Any):
        """ 
        runs all methods over and over again until there is no more updates based on current available model values
        for the given `property_name` and `value`
        """
        self.updates(session_id, model_id, {property_name: value})

    def lookup_table(self, table_name : str) -> pd.DataFrame:
        buf : Buffer = self._agent.get_buffer(table_name)
        if  buf:
            df = pd.DataFrame(buf.data())
            return df    
        else:
            return None

    def get_data_model(self, session_id : str, model_id : str) -> DataModel:
        session = self._sessions[session_id]
        if session:
            model = session.get_model(model_id)
            return model
        else:
            return None
    
    def get_data_models(self, session_id : str = None) -> list[str]:
        session = self._sessions[session_id]
        if session:
            return list(session.get_model_ids())
        else:
            return []            
    
    def get_source(self, model_class : str) -> str:
        if model_class in self._handlers:            
            return Path(self._handlers[model_class].get_model_path()).read_text(encoding="utf-8")
        else:
            logger.error(f"No ModelHandler for class {model_class} was registered")
            return None

