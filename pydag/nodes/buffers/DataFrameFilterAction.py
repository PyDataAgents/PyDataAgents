from dataclasses import dataclass, field

from ...utils.DataUtils import DataUtils
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class DataFrameFilterAction(BufferNode, Action):
    
    row_filter : str = field(default=None, metadata={"description": "pandas filter command to apply to filter the rows of the buffer converted to dataframe"})
    column_filter : list[str] = field(default_factory=list, metadata={"description": "list of columns to filter for"})        
    
    def _on_execute(self):
        data = self.get_parent_data()
        df = DataUtils.dict_to_dataframe(data)
        df_filtered = df.query(self.row_filter)
        df_filtered = df_filtered[self.column_filter]
        data_filtered = DataUtils.dataframe_to_dict(df_filtered)
        self.add_data(data_filtered)