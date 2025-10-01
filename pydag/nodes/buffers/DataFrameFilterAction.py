from dataclasses import dataclass, field

from ...utils.DataUtils import DataUtils
from ...buffers.DictBuffer import DictBuffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class DataFrameFilterAction(BufferNode, Action):
    
    row_filter : str = field(default=None, metadata={"description": "pandas filter command to apply to filter the rows of the buffer converted to dataframe"})
    column_filter : list[str] = field(default_factory=list, metadata={"description": "list of columns to filter for"})        
    
    def execute(self):
        for parent in self.parents:
            if not isinstance(parent, BufferNode):
                raise NodeException("parents must be of type " + BufferNode.cname())
            else:
                if not isinstance(parent.buffer, DictBuffer):
                    raise NodeException("parents' buffers must be of type " + DictBuffer.cname())
            data = parent.buffer.data(persistent=self.persistent, n=self.n)
            df = DataUtils.dict_to_dataframe(data)
            df_filtered = df.query(self.row_filter)
            df_filtered = df_filtered[self.column_filter]
            data_filtered = DataUtils.dataframe_to_dict(df_filtered)
            self.buffer.push(data_filtered)