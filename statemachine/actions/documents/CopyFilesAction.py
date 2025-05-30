from dataclasses import dataclass, field
from PyDataGrabber.buffers.ListBuffer import ListBuffer
from PyDataGrabber.statemachine.Action import Action
from PyDataGrabber.statemachine.BufferNode import BufferNode
from PyDataGrabber.statemachine.StatemachineException import StatemachineException
from PyDataGrabber.utils.FileUtils import FileUtils

@dataclass
class CopyFilesAction(BufferNode, Action):
    
    target_folder : str = field(default=None, metadata={"description": "target folder to copy all the files to in Buffer"})
    
    def __init__(self):
        super().__init__()        
        
    def execute(self):
        if FileUtils.exists_folder(self.target_folder):
            if isinstance(self.buffer, ListBuffer):
                data = self.buffer.data(n = 0, persistent = False)
                for file in data:
                    FileUtils.copy_file(file, self.target_folder)
            else:
                raise StatemachineException("Only " +ListBuffer.cname()+ " is supported for this " + self.cname())                      
        else:
            raise StatemachineException("folder " + self.target_folder + " does not exist")
        