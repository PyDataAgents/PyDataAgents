from dataclasses import dataclass, field

from ....agents.AgentConfig import AgentConfig
from ....agents.Agent import Agent
from ....buffers.ListBuffer import ListBuffer
from ...Action import Action
from ...BufferNode import BufferNode
from ....statemachine.NodeException import NodeException
from ...StatemachineException import StatemachineException
from ....utils.FileUtils import FileUtils

@dataclass
class MoveFilesAction(BufferNode, Action):
    """`Action` that moves files to a new `target_folder`
    <br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variable

    Raises:
        StatemachineException: if folder does not exist or wrong `Buffer` is provided
    """
    
    target_folder : str = field(default=None, metadata={"description": "target folder to move all the files to in Buffer"})
    
    def install(self, agent : Agent = None):
        Action.install(self, agent)
        if agent is not None:
            if self.buffer_id is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
                else:
                    raise NodeException("no buffer_id='" + self.buffer_id + "' was found in " + Agent.cname())
    
    def execute(self):
        if FileUtils.exists_folder(self.target_folder):
            if self.buffer is None:
                parent_buffer_found : bool = False
                for parent in self.parents:
                    if isinstance(parent.buffer, ListBuffer):
                        parent_buffer_found = True
                        data = parent.buffer.data(n = 0, persistent = False)
                        for file in data[AgentConfig.VALUES]:
                            FileUtils.move_file(file, self.target_folder)
                if not parent_buffer_found:
                    raise StatemachineException("No " + ListBuffer.cname() + "s in parent were found. Only " +ListBuffer.cname()+ " is supported for this " + self.cname())   
            else:
                if isinstance(self.buffer, ListBuffer):
                    data = self.buffer.data(n = 0, persistent = False)
                    for file in data[AgentConfig.VALUES]:
                        FileUtils.move_file(file, self.target_folder)
                else:
                    raise StatemachineException("Only " +ListBuffer.cname()+ " is supported for this " + self.cname())                      
        else:
            raise StatemachineException("folder " + self.target_folder + " does not exist")
        