from dataclasses import dataclass, field
from ...buffers.ListBuffer import ListBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..StatemachineException import StatemachineException
from ...utils.FileUtils import FileUtils

@dataclass
class ListFilesAction(BufferNode, Action):
    
    folder : str = field(default=None, metadata={"description": "folder to list the files from into a Buffer"})
    pattern : str = field(default=None, metadata={"description": "pattern to look for in file names"})
    extension : str = field(default=None, metadata={"description": "extension to include"})
    newer_than_seconds : int = field(default=None, metadata={"description": "specifies how old in seconds a file can be to be included"})
    recursive : bool = field(default=False, metadata={"description": "specifies whether to search subdirectories aswell"})
    
    def __init__(self):
        super().__init__()
        
    def execute(self):
        if FileUtils.exists_folder(self.folder):
            if isinstance(self.buffer, ListBuffer):
                files = FileUtils.list_files(self.folder, self.pattern, self.extension, self.newer_than_seconds, self.recursive)
                self.buffer.push(files)
            else:
                raise StatemachineException("Only " +ListBuffer.cname()+ " is supported for this " + self.cname())                      
        else:
            raise StatemachineException("folder " + self.folder + " does not exist")    