from dataclasses import dataclass, field

from ....buffers.DataType import DataType
from ....buffers.ListBuffer import ListBuffer
from ....agents.Agent import Agent
from ....utils.BufferUtils import BufferUtils
from ....buffers.DictBuffer import DictBuffer
from ...StatemachineException import StatemachineException
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class FormattedStringAction(BufferNode, Action):
    """
    `Action` to compose a formatted string and store it in this `Action`'s buffer
    using its parent's buffer to create the new string
    """
    
    data_keys : list[str] = field(default_factory=list, metadata={"description": "list of keys to use to compose the formatted string"})
    template : str = field(default=None, metadata={"description": "string template to insert the data from the parent buffer into, e.g. 'Hi {}, are you from {}'"})
    
    def __init__(self):
        super().__init__()
        
    def install(self, agent : Agent = None):
        if self.buffer is None:
            if agent is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
            else:
                self.buffer = ListBuffer()
                self.buffer.capacity = -1
                self.buffer.data_type = DataType.STRING
        
    def execute(self):
        # check if template and data keys match
        if len(self.data_keys) == self.template.count("{}"):            
            for parent in self.parents:
                if not isinstance(parent, BufferNode):
                    raise StatemachineException("parents must be of type " + BufferNode.cname())
                else:
                    if not isinstance(parent.buffer, DictBuffer):
                        raise StatemachineException("parents' buffers must be of type " + DictBuffer.cname())
                d = parent.buffer.data(persistent=False)
                rows = BufferUtils.dict_to_list(d)
                for row in rows:
                    td : list = []
                    s : str = ""
                    for dk in self.data_keys:
                        td.append(row[dk])
                    s = self.template.format(*td)            
                    self.buffer.push(s)
        else:
            raise StatemachineException(f"number of data_keys({len(self.data_keys)}) and placeholders ({self.template.count('{}')}) in template do not match")