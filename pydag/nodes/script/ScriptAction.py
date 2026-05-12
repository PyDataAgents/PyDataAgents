from dataclasses import dataclass, field
from loguru import logger

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
    output_keys : list[str] = field(default_factory=list, metadata={"description": "keys to extract from the script and store their values into this element's buffer. If empty, no data is stored in the buffer."})    
    use_parent_data: bool = field(default=True, metadata={"description": "whether to use data from parent buffers. If set to false, the script will only receive data from its own buffer. This can be useful if you want to execute a script that does not depend on parent data, but you still may want to use the output_keys to store data in the buffer."})

    def __post_init__(self):
        super().__post_init__()
        self._code : str = None
        
    def _on_install(self, agent : Agent = None):
        BufferNode._on_install(self, agent)
        if self.use_parent_data:
            if len(self.input_keys) == 0:
                raise NodeException("input_keys must be provided if use_parent_data is True.")
        if self.script_path:
            if FileUtils.exists_file(self.script_path):
                with open(self.script_path, 'r', encoding='utf-8') as file:
                    self._code = file.read()
            else:
                raise NodeException("Script file " + self.script_path + " does not exist.")
        else:
            raise NodeException("Script file path must be provided.")
        
    def _on_execute(self):
        # generate local scope for script execution
        local_scope = self.get_parent_data() if self.use_parent_data else {}
        # Data was in Parent Buffer but no matching input_keys found.
        if self.use_parent_data and len(local_scope) == 0:
            logger.debug("no input data found in parent buffers for specified input_keys, executing script with empty local scope")
        try:
            exec(self._code, {}, local_scope)
        except Exception as e:
            logger.error(f"Error executing script in {self.name()}: {e}")
            #raise NodeException(f"Error executing script: {e}") # It might be the case, that a script fails due to wrong input data, but we do not want the whole agent to fail because of that. So we catch the exception and log it, but we do not raise it further.
        out = {}
        for key in self.output_keys:
            if key in local_scope:
                out[key] = local_scope[key]
        if len(out) == 0:
            logger.debug("no output data found from script for specified output_keys, no data will be added to buffer")
        else:
            self.add_data(out)
            
        
    
    
