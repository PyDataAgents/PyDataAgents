from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ..BufferNode import BufferNode
from ..Action import Action
from ..NodeException import NodeException


@dataclass
class ScriptAction(BufferNode, Action):
    """
    `Action` for executing a custom script to process data from the parents' `Buffer`s and to store the processed data back into this `Buffer`.
    The script must be a valid Python code snippet that runs properly.
    The function takes the current buffer data and injects data from it by the specified `input_keys`.
    The same way the `Action`returns data by the specified `output_keys` back to its `Buffer`.
    """
    
    script_path : str = field(default=None, metadata={"description": "Python code snippet defining a script to process buffer data"})
    input_keys : list[str] = field(default_factory=list, metadata={"description": "keys to search for in parent buffers and inject their values into the script"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "keys to extract from the script and store their values into this element's buffer"})    
    persistent : bool = field(default=True, metadata={"description": "specifies whether to keep the extracted data in origin buffer"})
    n : int = field(default=0, metadata={"description": "number of samples to extract from buffer, default 0 extracts all"})
        
    def __post_init__(self):
        super().__post_init__()
        self.code : str = None
        
    def install(self, agent : Agent = None):
        super().install(agent)
        if self.script_path:
            with open(self.script_path, 'r', encoding='utf-8') as file:
                self.code = file.read()
        else:
            raise NodeException("Script file path must be provided.")
        
    def execute(self):
        # generate local scope for script execution
        local_scope = {}
        for parent in self.parents:
            if not isinstance(parent, BufferNode):
                raise NodeException("parents must be of type " + BufferNode.cname())
            
            d = parent.buffer.data(persistent=self.persistent, n=self.n)
        
    
    