from dataclasses import dataclass, field


from ...agents.Agent import Agent
from ...utils.DataUtils import DataUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class DataFrameFilterAction(BufferNode, Action):
    
    row_filter : str = field(default=None, metadata={"description": "pandas filter command to apply to filter the rows of the buffer converted to dataframe"})
    column_filter : list[str] = field(default_factory=list, metadata={"description": "list of columns to filter for"})        
    
    def _on_install(self, agent : Agent = None):
        super()._create_default_buffer(agent, timestamps_enabled=False, index_enabled=False)
        if len(self.column_filter) == 0 and not self.row_filter:
            raise NodeException("Either column_filter is specified or row_filter must be specified.")
        
    def _on_execute(self):
        data = self.get_parent_data()
        df = DataUtils.dict_to_dataframe(data)
        df_filtered = df.query(self.row_filter)
        if len(self.column_filter) > 0:
            df_filtered = df_filtered[self.column_filter]
        data_filtered = DataUtils.dataframe_to_dict(df_filtered)
        self.add_data(data_filtered)