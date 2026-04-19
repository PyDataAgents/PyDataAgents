from dataclasses import dataclass, field
import pandas as pd


from ...utils.DataUtils import DataUtils
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class PivotAction(BufferNode, Action):
    """ A `BufferNode` thats builds a pivot table from parent node data and emits the result as records.		
    """
    
    index : str | list = field(default_factory=list, metadata={"description": "Column name(s) to use as the pivot table index"})
    columns : str | list = field(default_factory=list, metadata={"description": "columns (str | list): Column name(s) to use to create pivoted columns"})
    values : str | list = field(default_factory=list, metadata={"description": "Column name(s) whose values are aggregated in the pivot"})
    aggfunc : str | list = field(default_factory=list, metadata={"description": "Aggregation function(s) applied to `values`"})
    
    def _on_execute(self):
        data = self.get_parent_data()
        df : pd.DataFrame = DataUtils.dict_to_dataframe(data)        
        
        if isinstance(self.values, str):
            values = [self.values]
        else:
            values = self.values
        
        pivot = df.pivot_table(
            index=self.index,
            columns=self.columns,
            values=values,
            aggfunc=self.aggfunc
        )
        
        # Fill missing values if needed
        #pivot = pivot.fillna(0)
        
        if isinstance(pivot.columns, pd.MultiIndex):
            pivot.columns = [
                "_".join([str(c) for c in col if c != ""])
                for col in pivot.columns
            ]
        result = pivot.reset_index().to_dict(orient="records")
        self.add_data(result)