from dataclasses import dataclass, field
from typing import Union
from loguru import logger

from ...agents.AgentConfig import AgentConfig
from ...agents.Agent import Agent
from ..NodeException import NodeException
from ...buffers.ListBuffer import ListBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ...utils.FileUtils import FileUtils

@dataclass
class ListFilesAction(BufferNode, Action):
    
    folder : str = field(default=None, metadata={"description": "folder to list the files from into a Buffer"})
    pattern : Union[str |list[str]] = field(default=None, metadata={"description": "pattern to look for in file names, can be str or list, e.g. ['png', 'jpg']"})
    extension : str = field(default=None, metadata={"description": "extension to include"})
    newer_than_seconds : int = field(default=None, metadata={"description": "specifies how old in seconds a file can be to be included"})
    recursive : bool = field(default=False, metadata={"description": "specifies whether to search subdirectories aswell"})
        
    def _on_install(self, agent : Agent = None):
        """ installs a `ListBuffer` if no buffer is specified

        Args:
            agent (Agent, optional): agent object. Defaults to None.
        """
        if agent is not None:
            buf = agent.get_buffer(self.buffer_id)                
            if buf:
                self._buffer = buf
            else:
                self._buffer = ListBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY)
                self.buffer_id = self._buffer.id
                self._buffer.install(agent)
                agent.add_buffer(self._buffer)
        else:
            self._buffer = ListBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY)
            self.buffer_id = self._buffer.id
            self._buffer.install(agent)
            
    def _on_execute(self):
        if FileUtils.exists_folder(self.folder):
            if isinstance(self._buffer, ListBuffer):
                files = FileUtils.list_files(self.folder, self.pattern, self.extension, self.newer_than_seconds, self.recursive)
                #logger.debug(f"Found files {files} in {self.folder}")
                self.add_data(files)
            else:
                raise NodeException("Only " + ListBuffer.cname() + " is supported for this " + self.cname())
        else:
            raise NodeException("folder " + self.folder + " does not exist")    