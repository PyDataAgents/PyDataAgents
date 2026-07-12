from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from pydag.services.datamodel.DataModel import DataModel


@dataclass
class TableDataModel(DataModel):
    """ Test Table Data Model    
    """
    
    table : list[dict[str, Any]] = field(default_factory=list, metadata={"description": "test table", "ui_type": "table", "ui_options": {"columns": {"A": "Column A", "B": "Column B"}}})
    tsum : float = field(default=None, metadata={"description" : "sum of the first table column"})
    
    def compute_sum(self):
        df : pd.DataFrame = pd.DataFrame(self.table)
        self.tsum = df.iloc[:, 0].sum()