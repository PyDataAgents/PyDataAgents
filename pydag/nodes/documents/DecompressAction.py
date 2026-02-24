from dataclasses import dataclass, field


from ...utils.FileUtils import FileUtils
from ...nodes.Action import Action
from ...nodes.NodeException import NodeException


@dataclass
class DecompressAction(Action):
    """ `Action` that decompresses the specified `source_file` under the new filepath `target_dir`    
    """
    
    source_file : str = field(default=None, metadata={"description": "path of the source file for being compressed. If source_file is a folder, the whole folder will be compressed."})
    target_dir : str = field(default=None, metadata={"description": "new target filepath. If a folder is specified, the name of the source file is used. If no target filepath is specified, the file is compressed in place."})
    
    
    def _on_execute(self):
        try:
            FileUtils.decompress(self.source_file, self.target_dir)
        except FileNotFoundError as e:
            raise NodeException(f"Could not decompress {self.source_file} to {self.target_dir}") from e