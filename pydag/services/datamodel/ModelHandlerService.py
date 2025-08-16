import ast
from dataclasses import dataclass, field
import pandas as pd
from pathlib import Path

from ...utils.ClassUtils import ClassUtils
from ...services.ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ...agents.Agent import Agent
from ..Service import Service
from .DataModel import DataModel

@dataclass
class ModelHandlerService(Service):
    """
    Model execution / model handler
    this file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.
    This means that only those methods are executed whose variables have changed.
    The model handler also registers variable inputs (from outside) and then initiates the execution of methods accordingly.
    <br>
    <br>Example of a model file:
    ```python
    from pydag.services.datamodel.DataModel import DataModel
    
    def method1(dm : DataModel):
        dm.b = dm.a * 2 + 10.0
        dm.c = dm.a + dm.c
    
    def method2(dm : DataModel):
        dm.t = f"Hello World {dm.c}"
    ```
    <br>Example of a script file
    ```python
    from dataclasses import dataclass, field
    from pydag.services.datamodel.DataModel import DataModel

    @dataclass
    class SimpleDataModel(DataModel):
    
        a : float = field(default=None, metadata={"description": "variable 1"})
        b : float = field(default=None, metadata={"description": "variable 2"})
        c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})
        t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})
    ```
    <br>the script files always have to introduce the `DataModel` `dm` variable as first argument to each method
    """
    
    model_path : str = field(default=None, metadata={"description": "path of the model.py file"})
    model_name : str = field(default=None, metadata={"description": "name of the class to load from the model.py file"})
    script_path : str = field(default=None, metadata={"description": "path of the script.py file"})
    
    DATA_MODEL_KEY = "dm"
    
    def __post_init__(self):
        super().__post_init__()
        self.data_model : DataModel = None
        self.lookup_store : dict[str, pd.DataFrame] = None
        self.methods : dict = None
        self.method_input_vars : dict[str, list[str]] = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if not FileUtils.exists_file(self.model_path):
            raise ServiceException(f"No model file was found for '{self.model_path}'")
        if self.model_name is None:
            raise ServiceException("No model name was specified")
        if not FileUtils.exists_file(self.script_path):
            raise ServiceException(f"No script file was found for '{self.script_path}'")
        self.data_model = ClassUtils.load_instance(self.model_path, self.model_name)
        self.__find_methods()
        self.__find_method_input_vars()        
                
    def __find_methods(self):
        self.methods = ClassUtils.load_methods(self.script_path)
    
    def __find_method_input_vars(self):
        script_path = Path.resolve(self.script_path)
        source_code = script_path.read_text()
        # Parse file into AST
        tree = ast.parse(source_code)
        visitor = DataModelAccessVisitor()
        visitor.visit(tree)
        self.method_input_vars = visitor.read_accesses.items()


class DataModelAccessVisitor(ast.NodeVisitor):
    def __init__(self):
        self.read_accesses = {}   # function_name -> set of property names
        self.current_func = None

    def visit_FunctionDef(self, node):
        # track which function we are in
        self.current_func = node.name
        self.read_accesses[self.current_func] = set()
        self.generic_visit(node)
        self.current_func = None

    def visit_Attribute(self, node):
        # check for "data_model.something"
        if isinstance(node.value, ast.Name) and node.value.id == ModelHandlerService.DATA_MODEL_KEY:
            # Are we inside a store (= assignment target) or a read?
            if not isinstance(getattr(node, "ctx", None), ast.Store):
                self.read_accesses[self.current_func].add(node.attr)
        self.generic_visit(node)