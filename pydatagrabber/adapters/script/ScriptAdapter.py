from dataclasses import dataclass, field

from ...utils.FileUtils import FileUtils

from ...buffers.Buffer import Buffer
from ...adapters.ReadAdapter import ReadAdapter


@dataclass
class ScriptAdapter(ReadAdapter):
    """An `Adapter` that reads data from specified `Buffer`s using computations / transformations defined in a script file
    <br>new results are written back to specified output `Buffer`s
    """
    
    script_path : str = field(default=None, metadata={"description" : "path to the script to load and execute"})
    
    def __init__(self):
        super().__init__()
        
    def connect(self) -> bool:
        return FileUtils.exists_file(self.script_path)
    
    def disconnect(self):
        return True
    
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 0):
        pass