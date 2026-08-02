from dataclasses import dataclass, field
from loguru import logger

from ...agents.Agent import Agent
from ...buffers.ListBuffer import ListBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils

@dataclass
class MoveFilesAction(BufferNode, Action):
    """`Action` that moves files to a new `target_folder`
    <br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variable

    Raises:
        NodeException: if folder does not exist or wrong `Buffer` is provided
    """
    
    target_folder : str = field(default=None, metadata={"description": "target folder to move all the files to in Buffer"})
    
    def _on_install(self, agent : Agent = None):
        if agent is not None:
            if self.buffer_id is not None:
                buf = agent.get_buffer(self.buffer_id)                
                if buf:
                    self._buffer = buf
                else:
                    raise NodeException("no buffer_id='" + self.buffer_id + "' was found in " + Agent.__name__)
    
    def _on_execute(self):
        if FileUtils.exists_folder(self.target_folder):
            if self._buffer is None:
                data = self.get_parent_data()
                for value in data.values():
                    for file in value:
                        if FileUtils.exists_file(file):
                            logger.debug(f"Moving {file} to {self.target_folder}")
                            FileUtils.move_file(file, self.target_folder)
            else:
                if isinstance(self._buffer, ListBuffer):
                    data = self._buffer.data(n = 0, persistent = False)
                    if data is not None:
                        for files in data.values():
                            for file in files:
                                if FileUtils.exists_file(file):
                                    logger.debug(f"Moving {file} to {self.target_folder}")
                                    FileUtils.move_file(file, self.target_folder)
                else:
                    raise NodeException("Only " +ListBuffer.cname()+ " is supported for this " + self.cname())                      
        else:
            raise NodeException("folder " + self.target_folder + " does not exist")
        