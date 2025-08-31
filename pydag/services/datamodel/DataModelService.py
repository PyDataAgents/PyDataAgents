import ast
import inspect
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
    The model handler also registers variable inputs (from outside) and method outputs and then initiates the execution of methods accordingly.
    <br>
    <br>Example of a model file:
    ```python
    import pandas as pd
    from pydag.services.datamodel.DataModel import DataModel
    
    @dataclass
    class SimpleDataModel(DataModel):
    
        a : float = field(default=None, metadata={"description": "variable 1"})
        b : float = field(default=None, metadata={"description": "variable 2"})
        c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})
        t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})
    
        def method1(self):
            self.b = self.a * 2 + 10.0
            self.c = self.a + self.c
        
        def method2(self):
            self.t = f"Hello World {self.c}"
        
        def method3(self, dms : DataModelService):
            df = dms.lookup_table('NAME_OF_TABLE')
            values = df.query(f"COL1 > 30 and COL2 <= {self.a}")
            self.value = values["COL1"].to_list()[0]    
    
    ```
    
    <br>The model files always have to inherit from `DataModel`, they are `dataclasses` and all properties should be introduced as `fields`.
    <br>
    <br>As an additional argument to `DataModel` methods the argument `dms` of type `DataModelService` can be passed, which allows acces to the lookup-tables via dms.lookup_store([Name of the table]) with Pandas Dataframes can be provided in order to lookup values based on model variables
    """
    
    model_path : str = field(default=None, metadata={"description": "path of the model.py file"})
    model_name : str = field(default=None, metadata={"description": "name of the class to load from the model.py file"})
        
    def __post_init__(self):
        super().__post_init__()
        self.data_model : DataModel = None
        self.methods : dict = None
        self.method_input_vars : dict[str, list[str]] = None
        self.method_output_vars : dict[str, list[str]] = None
        self.method_arguments : dict[str, int] = {}
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if not FileUtils.exists_file(self.model_path):
            raise ServiceException(f"No model file was found for '{self.model_path}'")
        if self.model_name is None:
            raise ServiceException("No model name was specified")
        observer = DataModelObserver(self)
        self.data_model : DataModel = ClassUtils.load_instance(self.model_path, self.model_name)
        self.data_model.observer = observer
        self.__find_methods()
        self.__find_method_vars()

    def start(self):
        super().start()

    def stop(self):
        super().stop()

    def update(self, property_name, value):
        self.data_model.set_data(property_name, value)

    def run_model(self, blocked_vars : list[str] = None):
        """ 
        runs all methods over and over again until there is no more updates based on current available model values
        """
        last_success_methods = 0
        success_methods = self.__run_methods(blocked_vars)
         # run as long as the number of methods being run successful increases or all methods were run
        while success_methods > last_success_methods and success_methods is not len(self.methods):
            last_success_methods = success_methods
            success_methods = self.__run_methods(blocked_vars)

    def lookup_table(self, table_name : str) -> pd.DataFrame:
        if table_name in self.agent.buffer_store:
            df = pd.DataFrame(self.agent.get_buffer(table_name).data())
            return df    
        else:
            return None

    def __run_methods(self, blocked_vars : str = None) -> int:
        """ runs all methods once and returns how many were executed based on data model values availability
        """
        m : int = 0
        for name, method in self.methods.items():
            input_vars = self.method_input_vars[name]
            method_ready : bool = True
            # check if method is ready based on set inputs
            for input_var in input_vars:
                if not self.data_model.has_value(input_var):
                    method_ready = False
                    break
            if method_ready:
                # check if the method has output variables that are blocked
                for blocked_var in blocked_vars:
                    if not blocked_var in self.method_output_vars[name]:
                        # check whether to pass only model or lookup as well
                        if self.method_arguments[name] > 1:
                            method(self.data_model, self)
                        else:                 
                            method(self.data_model)
                        m = m + 1
        return m                
                
    def __find_methods(self):
        self.methods = ClassUtils.load_methods(self.model_path)
        for name, method in self.methods.items():
            sig = inspect.signature(method)
            params = sig.parameters
            num_args = len([
                p for p in params.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default == p.empty
            ])
            self.method_arguments[name] = num_args
    
    def __find_method_vars(self):
        script_path = Path(self.model_path).resolve()
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
        self.method_output_vars = write_vars
        # validate if method properties exist in model properties
        self.__validate_properties(all_vars)
        
    def __validate_properties(self, properties : set):
        for prop in properties:
            if not self.data_model.has_property(prop):
                raise ServiceException(f"the script calls a property '{prop}', that does not exist in the model")

class DataModelObserver():

    def __init__(self, model_service : DataModelService):
        self.model_service = model_service

    def observe(self, blocked_vars : list[str]= None):
        self.model_service.run_model(blocked_vars)


class DataModelReadAccessVisitor(ast.NodeVisitor):
    def __init__(self):
        self.read_accesses = {}   # function_name -> set of property names
        self.current_func = None
        self.current_class = None

    def visit_ClassDef(self, node):
        # Enter the class
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class  # restore previous class after leaving

    def visit_FunctionDef(self, node):
         # Only track methods inside a class
        if self.current_class is None:
            return
        # track which function we are in
        qualified_name = f"{self.current_class}.{node.name}"
        self.current_func = qualified_name
        self.read_accesses[qualified_name] = set()
        self.generic_visit(node)
        self.current_func = None

    def visit_Attribute(self, node):
        # check for "dm.something"
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            # Are we inside a store (= assignment target) or a read?
            if not isinstance(getattr(node, "ctx", None), ast.Store):
                if self.current_func:
                    self.read_accesses[self.current_func].add(node.attr)
        self.generic_visit(node)

class DataModelWriteAccessVisitor(ast.NodeVisitor):
    def __init__(self):
        self.write_accesses = {}   # function_name -> set of property names
        self.current_func = None
        self.current_class = None
    
    def visit_ClassDef(self, node):
        # Enter the class
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class  # restore previous class after leaving 

    def visit_FunctionDef(self, node):
        if self.current_class is None:
            return
        # Track the current function (with class)
        qualified_name = f"{self.current_class}.{node.name}"
        self.current_func = qualified_name
        self.write_accesses[qualified_name] = set()
        self.generic_visit(node)
        self.current_func = None

    def visit_Attribute(self, node):
        # check for "dm.something"
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            # Are we inside a store (= assignment target) or a read?
            if isinstance(getattr(node, "ctx", None), ast.Store):
                if self.current_func:
                    self.write_accesses[self.current_func].add(node.attr)
        self.generic_visit(node)