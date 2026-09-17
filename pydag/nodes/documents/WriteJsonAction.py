from dataclasses import dataclass, field
import json
from loguru import logger

from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode


@dataclass
class WriteJsonAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the json file to write the data to"})
    file_path_key : str = field(default=None, metadata={"description": "specifies a key for the file_path to look within parent data"})
    encoding : str = field(default="utf-8", metadata={"description": "name of the file encoding to use, e.g. utf-8 (default), utf-16, ..."})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.file_path is None:
            if self.file_path_key is None:
                raise NodeException("Whether file_path nor file_path_key were provided")
        if self.file_path and self.file_path_key:
            logger.warning("Both file_path and file_path_key were provided, only file_path_key is considered.")
    
    def _on_execute(self):
        d = self.get_parent_data(by_rows=True)
        if len(d) > 0:
            if self.file_path_key:
                if self.file_path_key in d[0]:
                    row : dict
                    for row in d:
                        fp : str = row[self.file_path_key]                        
                        with open(self.file_path, encoding=self.encoding, mode="+w") as f:
                            json.dump(row, fp=f, indent=4, ensure_ascii=False)
                else:
                    raise NodeException(f"file_path_key {self.file_path_key} is not contained in parent data")
            else:
                if self.file_path:
                    with open(self.file_path, encoding=self.encoding, mode="+w") as f:
                        json.dump(d, fp=f, indent=4, ensure_ascii=False)
                    
        
    