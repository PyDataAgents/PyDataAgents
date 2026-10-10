from dataclasses import dataclass, field

from ..NodeException import NodeException
from ..Action import Action
from ..BufferNode import BufferNode
from ...utils.FileUtils import FileUtils

@dataclass
class CopyFilesAction(BufferNode, Action):
    
    target_folder : str = field(default=None, metadata={"description": "target folder to copy all the files to in Buffer"})
    create_missing_dir : bool = field(default=True, metadata={"description": "create the target folder if it does not exist"})
           
    def _on_execute(self):
        if self.create_missing_dir:
            FileUtils.create_dir(self.target_folder)
        else:
            raise NodeException("folder " + self.target_folder + " does not exist")
        data = self.get_parent_data(by_rows = True)
        for row in data:
            for k, v in row.items():
                if isinstance(v, str) and FileUtils.exists_file(v):
                    file = v
                    FileUtils.copy_file(file, self.target_folder)