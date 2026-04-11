from dataclasses import dataclass, field
import pandas as pd


from ...utils.DataUtils import DataUtils
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class PivotAction(BufferNode, Action):
    
    index : str | list = field(default_factory=None)
    columns : str | list = field(default_factory=None)
    values : str | list = field(default_factory=None)
    aggfunc : str | list = field(default_factory=None)
    
    def _on_execute(self):
        data = self.get_parent_data()
        df : pd.DataFrame = DataUtils.dict_to_dataframe(data)        
        
        if isinstance(values, str):
            values = [values]
        
        pivot = df.pivot_table(
            index=self.index,
            columns=self.columns,
            values=self.values,
            aggfunc=self.aggfunc
        )
        
        # Fill missing values if needed
        pivot = pivot.fillna(0)
        
        if isinstance(pivot.columns, pd.MultiIndex):
            pivot.columns = [
                "_".join([str(c) for c in col if c != ""])
                for col in pivot.columns
            ]
        result = pivot.reset_index().to_dict(orient="records")
        self.add_data(result)