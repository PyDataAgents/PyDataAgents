from dataclasses import dataclass, field
import os
from loguru import logger


from ...utils.DataUtils import DataUtils
from ...buffers.Buffer import Buffer
from ...utils.FileUtils import FileUtils
from ..NodeException import NodeException
from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class HTMLFileAction(BufferNode, Action):
    
    path : str = field(default=None, metadata={"description": "output folder or filepath to write the HTML files to, if a file is specified, then all html strings retrieved are (over)written to this location, if a folder is specified, then all html strings are written to files in this folder with the name schema <key>_<COUNTER>.html"})
    encoding : str = field(default="utf-8", metadata={"description": "encoding for html file(s), defalts to utf-8"})
    output_keys : list[str] = field(default_factory=lambda: ["path"], metadata={"description": "default output_keys are 'path', for this node only ever one output key is required"})
    
    def __post_init__(self):
        super().__post_init__()
        self._count : int = 0
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._count = 0
        
    def _on_execute(self):
        data = self.get_parent_data()
        if isinstance(data, list):
            data = DataUtils.list_to_dict(data)
        for k, values in data.items():
            if isinstance(values, list):
                for val in values:
                    if isinstance(val, str):
                        if FileUtils.exists_folder(self.path):
                            file_path : str = self.path + os.sep + k + "_" + str(self._count) + ".html"
                            with open(file_path, "w", encoding=self.encoding) as f:
                                f.write(val)
                            self._count += 1
                            self.add_data({self.output_keys[0]: file_path})   
                        else:
                            with open(self.path, "w", encoding=self.encoding) as f:
                                f.write(val)
                            self.add_data({self.output_keys[0]: self.path})
                    else:
                        logger.debug(f"parent {Buffer.__name__} data contains non-string values ({val})")
            else:
                raise NodeException(f"Unexpected datatype in {self.__class__.__name__}")