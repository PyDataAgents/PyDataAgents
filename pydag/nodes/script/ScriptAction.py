from dataclasses import dataclass, field

from pydag.utils.FileUtils import FileUtils

from ...agents.Agent import Agent
from ..BufferNode import BufferNode
from ..Action import Action
from ..NodeException import NodeException


@dataclass
class ScriptAction(BufferNode, Action):
    """
    `Action` for executing a custom script to process data from the parents' `Buffer`s and to store the processed data back into this `Buffer`.
    <br>The script must be a valid Python code snippet that runs properly.
    <br>The function takes the current buffer data and injects data from it by the specified `input_keys`.
    <br>The same way the `Action`returns data by the specified `output_keys` back to its `Buffer`.
    <br>Note that the script is executed in its own local scope, so variables defined in the script do not interfere with variables outside the script.
    <br>Also note that all output variables should be converted to primitives (e.g. int, float, str, list, dict) or list of primitives inside the script. Do not leave them as numpy arrays or dataframes.
    """
    
    script_path : str = field(default=None, metadata={"description": "Python code snippet defining a script to process buffer data"})
    input_keys : list[str] = field(default_factory=list, metadata={"description": "keys to search for in parent buffers and inject their values into the script"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "keys to extract from the script and store their values into this element's buffer"})    
       
    def __post_init__(self):
        super().__post_init__()
        self.code : str = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if self.script_path:
            if FileUtils.exists_file(self.script_path):
                with open(self.script_path, 'r', encoding='utf-8') as file:
                    self.code = file.read()
            else:
                raise NodeException("Script file " + self.script_path + " does not exist.")
        else:
            raise NodeException("Script file path must be provided.")
        
    def execute(self):
        # generate local scope for script execution
        local_scope = {}
        for parent in self.parents:
            if not isinstance(parent, BufferNode):
                raise NodeException("parents must be of type " + BufferNode.cname())
            
            d = parent.buffer.data(persistent=self.persistent, n=self.n)
            for key in self.input_keys:
                if key in d:
                    local_scope[key] = d[key]        
        if len(local_scope) == 0:
            raise NodeException("no input data found in parent buffers for specified input_keys")
        exec(self.code, {}, local_scope)
        out = {}
        for key in self.output_keys:
            if key in local_scope:
                out[key] = local_scope[key]
        if len(out) == 0:
            raise NodeException("no output data found from script for specified output_keys")
        self.buffer.push(out)
            
        
    
    