import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import pandas as pd

from ...utils.ClassUtils import ClassUtils
from ..ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ...agents.Agent import Agent
from ..Service import Service

if TYPE_CHECKING:
    from .DataModel import DataModel

@dataclass
class DataModelService(Service):
    """ `Service` that enables modeling of data, in terms of script based computations on complex data relationships (e.g. to model machine elements or similar)
    <br>Model execution / model handler
    this file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.
    This means that only those methods are executed whose variables have changed.
    The model handler also registers variable inputs (from outside) and then initiates the execution of methods accordingly.
    <br>
    <br>Example of a model file:
    ```python
    import pandas as pd
    from pydag.services.datamodel.DataModel import DataModel
    
    def method1(dm : DataModel):
        dm.b = dm.a * 2 + 10.0
        dm.c = dm.a + dm.c
    
    def method2(dm : DataModel):
        dm.t = f"Hello World {dm.c}"
       
    def method3(dm: DataModel, lookup_store : dict[str, pd.DataFrame]):
        df = lookup_store['NAME_OF_TABLE']
        values = df.query(f"COL1 > 30 and COL2 <= {dm.a}")
        dm.value = values["COL1"].to_list()[0]    
    
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
    <br>as an additional argument a lookup_store with Pandas Dataframes can be provided in order to lookup values based on model variables, the lookupstore is passed as second argument
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
        observer = DataModelObserver(self)
        self.data_model : DataModel = ClassUtils.load_instance(self.model_path, self.model_name)
        self.data_model.observer = observer
        self.__find_methods()
        self.__find_method_input_vars()

    def start(self):
        super().start()

    def stop(self):
        super().stop()

    def update(self, property_name, value):
        self.data_model.set_data(property_name, value)

    def run_model(self):
        """ 
        runs all methods over and over again until there is no more updates based on current available model values
        """
        last_success_methods = 0
        success_methods = self.__run_methods()
         # run as long as the number of methods being run successful increases or all methods were run
        while success_methods > last_success_methods and success_methods is not len(self.methods):
            last_success_methods = success_methods
            success_methods = self.__run_methods()

    def __run_methods(self) -> int:
        """ runs all methods once and returns how many were executed based on data model values availability
        """
        m : int = 0
        for name, method in self.methods.items():
            input_vars = self.method_input_vars[name]
            method_ready : bool = True
            for input_var in input_vars:
                if not self.data_model.has_value(input_var):
                    method_ready = False
                    break
            if method_ready:
                
                method(self.data_model)
                m = m + 1
        return m                
                
    def __find_methods(self):
        self.methods = ClassUtils.load_methods(self.script_path)
    
    def __find_method_input_vars(self):
        script_path = Path(self.script_path).resolve()
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
        self.method_input_vars = read_vars
        # validate if method properties exist in model properties
        self.__validate_properties(all_vars)
        
    def __validate_properties(self, properties : set):
        for prop in properties:
            if not self.data_model.has_property(prop):
                raise ServiceException(f"the script calls a property '{prop}', that does not exist in the model")

class DataModelObserver():

    def __init__(self, model_service : DataModelService):
        self.model_service = model_service

    def observe(self):
        self.model_service.run_model()


class DataModelReadAccessVisitor(ast.NodeVisitor):
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
        if isinstance(node.value, ast.Name) and node.value.id == DataModelService.DATA_MODEL_KEY:
            # Are we inside a store (= assignment target) or a read?
            if not isinstance(getattr(node, "ctx", None), ast.Store):
                self.read_accesses[self.current_func].add(node.attr)
        self.generic_visit(node)

class DataModelWriteAccessVisitor(ast.NodeVisitor):
    def __init__(self):
        self.write_accesses = {}   # function_name -> set of property names
        self.current_func = None

    def visit_FunctionDef(self, node):
        # track which function we are in
        self.current_func = node.name
        self.write_accesses[self.current_func] = set()
        self.generic_visit(node)
        self.current_func = None

    def visit_Attribute(self, node):
        # check for "data_model.something"
        if isinstance(node.value, ast.Name) and node.value.id == DataModelService.DATA_MODEL_KEY:
            # Are we inside a store (= assignment target) or a read?
            if isinstance(getattr(node, "ctx", None), ast.Store):
                self.write_accesses[self.current_func].add(node.attr)
        self.generic_visit(node)