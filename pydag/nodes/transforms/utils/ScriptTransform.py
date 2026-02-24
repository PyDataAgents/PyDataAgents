from dataclasses import dataclass, field

from pydag.agents.Agent import Agent
from pydag.nodes.NodeException import NodeException

from ...transforms.Transform import Transform


DEFAULT_VAL = 0.0 # used for missing context variables
    
@dataclass
class ScriptTransform(Transform):
    """
    `Transform` that executes a user-defined script that transforms or computes based on the input data.
    """
    
    script_file : str = field(default=None, metadata={"description": "Path to the script file to be executed."})
    context_variables : list[str] = field(default_factory=list, metadata={"description": "List of context variables to be used in the script."})
    output_variables : list[str] = field(default_factory=list, metadata={"description": "List of output variables produced by the script."})
    
    
    def __post_init__(self):
        super().__post_init__()
        self.code = None
        self.context : dict = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if self.script_file:
            with open(self.script_file, 'r', encoding='utf-8') as file:
                self.code = file.read()
        else:
            raise NodeException("Script file path must be provided.")
        
    def transform(self, data : dict) -> dict:
        if not self.code:
            raise NodeException("Script code is not loaded. Please call install() first.")
        
        # Prepare the execution context
        if self.context is None:
            self.context = {var: data.get(var, DEFAULT_VAL) for var in self.context_variables}
        else:
            for key in data.keys():
                self.context[key] = data.get(key, DEFAULT_VAL)
        
        # turn lists of length 1 into single values
        for key, value in self.context.items():
            if isinstance(value, list) and len(value) == 1:
                self.context[key] = value[0]
        
        # Execute the script
        try:
            exec(self.code, {}, self.context)
        except Exception as e:
            raise NodeException(f"Error executing script: {e}") from e
        
        # Collect output variables
        output_data = {var: self.context.get(var, DEFAULT_VAL) for var in self.output_variables}
        
        return output_data