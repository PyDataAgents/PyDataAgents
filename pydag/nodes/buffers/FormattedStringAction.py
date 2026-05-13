from dataclasses import dataclass, field
import re

from ..NodeException import NodeException
from ...utils.DataUtils import DataUtils
from ...buffers.DataType import DataType
from ...buffers.ListBuffer import ListBuffer
from ...buffers.DictBuffer import DictBuffer
from ...agents.Agent import Agent
from ...agents.AgentConfig import AgentConfig
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class FormattedStringAction(BufferNode, Action):
    """
    `Action` to compose a formatted string and store it in this `Action`'s buffer
    using its parent's buffer to create the new string
    """
    
    template : str = field(default=None, metadata={"description": "string template to insert the data from the parent buffer into, e.g. 'Hi {}, are you from {}'"})
                
    def _on_install(self, agent : Agent = None):
        if self._buffer is None:
            if agent is not None:
                if self.buffer_id is not None:
                    buf = agent.get_buffer(self.buffer_id)
                    if buf:
                        self._buffer = buf
                        self.buffer_id = buf.id
                else:
                    if len(self.output_keys) == 1:
                        self._buffer = DictBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY, data_type=DataType.STRING)
                    else:
                        self._buffer = ListBuffer(id=self.id + "-BUFFER", capacity=AgentConfig.INFINITE_CAPACITY, data_type=DataType.STRING)
                    self.buffer_id = self._buffer.id
                    self._buffer.install(agent)
                    agent.add_buffer(self._buffer)                
            else:
                if len(self.output_keys) == 1:
                    self._buffer = DictBuffer()
                else:
                    self._buffer = ListBuffer()
                self._buffer.install(agent)
                self._buffer.capacity = AgentConfig.INFINITE_CAPACITY
                self._buffer.data_type = DataType.STRING
        
    def _on_execute(self):
        # check if template and data keys match
        # Match with either the occurences of a number inside {}, or empty {}
        empty_brackets = self.template.count("{}")
        number_brackets = len(set(re.findall(r'\{\d+\}', self.template)))
        if len(self.input_keys) == empty_brackets or len(self.input_keys) == number_brackets:            
            data = self.get_parent_data()
            rows = DataUtils.dict_to_list(data)
            for row in rows:
                td = list(row.values())
                s = self.template.format(*td)            
                if len(self.output_keys) == 1:
                    dic = {self.output_keys[0]: s}
                    self.add_data(dic)
                else:
                    self.add_data(s)
        else:
            raise NodeException(f"number of input_keys({len(self.input_keys)}) and placeholders ({self.template.count('{}')}) in template do not match")
        
