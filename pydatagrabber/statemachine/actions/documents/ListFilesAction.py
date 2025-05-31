from dataclasses import dataclass, field
from PyDataGrabber.pydatagrabber.buffers.ListBuffer import ListBuffer
from PyDataGrabber.pydatagrabber.statemachine.Action import Action
from PyDataGrabber.pydatagrabber.statemachine.BufferNode import BufferNode
from PyDataGrabber.pydatagrabber.statemachine.StatemachineException import StatemachineException
from PyDataGrabber.pydatagrabber.utils.FileUtils import FileUtils

@dataclass
class ListFilesAction(BufferNode, Action):
    
    folder : str = field(default=None, metadata={"description": "folder to list the files from into a Buffer"})
    pattern : str = field(default=None, metadata={"description": "paatern to look for in file names"})
    extension : str = field(default=None, metadata={"description": "extension to include"})
    newer_than_seconds : int = field(default=None, metadata={"description": "specifies how old in seconds a file can be to be included"})
    
    def __init__(self):
        super().__init__()
        
    def execute(self):
        if FileUtils.exists_folder(self.folder):
            if isinstance(self.buffer, ListBuffer):
                files = FileUtils.list_files(self.folder, self.pattern, self.extension, self.newer_than_seconds)
                self.buffer.push(files)
            else:
                raise StatemachineException("Only " +ListBuffer.cname()+ " is supported for this " + self.cname())                      
        else:
            raise StatemachineException("folder " + self.folder + " does not exist")    