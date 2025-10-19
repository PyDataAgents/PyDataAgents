from dataclasses import dataclass, field
import re

from ..NodeException import NodeException
from ...utils.DataUtils import DataUtils
from ...buffers.DataType import DataType
from ...buffers.ListBuffer import ListBuffer
from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class FormattedStringAction(BufferNode, Action):
    """
    `Action` to compose a formatted string and store it in this `Action`'s buffer
    using its parent's buffer to create the new string
    """
    
    data_keys : list[str] = field(default_factory=list, metadata={"description": "list of keys to use to compose the formatted string"})
    template : str = field(default=None, metadata={"description": "string template to insert the data from the parent buffer into, e.g. 'Hi {}, are you from {}'"})
                
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
        # Match with either the occurences of a number inside {}, or empty {}
        empty_brackets = self.template.count("{}")
        number_brackets = len(set(re.findall(r'\{\d+\}', self.template)))
        if len(self.data_keys) == empty_brackets or len(self.data_keys) == number_brackets:            
            for parent in self.parents:
                if not isinstance(parent, BufferNode):
                    raise NodeException("parents must be of type " + BufferNode.cname())
                else:
                    if not isinstance(parent.buffer, DictBuffer):
                        raise NodeException("parents' buffers must be of type " + DictBuffer.cname())
                d = parent.buffer.data(persistent=self.persistent)
                if d is None:
                    continue
                else:
                    rows = DataUtils.dict_to_list(d)
                    for row in rows:
                        td : list = []
                        s : str = ""
                        for dk in self.data_keys:
                            td.append(row[dk])
                        s = self.template.format(*td)            
                        self.buffer.push(s)
        else:
            raise NodeException(f"number of data_keys({len(self.data_keys)}) and placeholders ({self.template.count('{}')}) in template do not match")
        