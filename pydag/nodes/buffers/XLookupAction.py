from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from ...agents.Agent import Agent
from ...utils.DataUtils import DataUtils
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class XLookupAction(BufferNode, Action):
    """ `BufferNode`, that extracts an exact-match lookup result asd on specified columns to lookup and return from parent buffer data.

    The first matching entry in `lookup_column` is used, like Excel's
    XLOOKUP/XVERWEIS with exact matching and first-to-last search.
    """

    lookup_values : list[Any] = field(default_factory=list, metadata={"description": "list of values to look up"})    
    lookup_column: str = field(default=None, metadata={"description": "parent-data column to search for each lookup value"})    
    return_column : str = field(default=None, metadata={"description": "parent-data column providing the matched result"})    
    not_found_value: Any = field(default=None, metadata={"description": "value to use when a lookup value has no match"})

    def _on_install(self, agent: Agent = None):
        self._create_default_buffer(agent, timestamps_enabled=False, index_enabled=False)
        if not self.lookup_column:
            raise NodeException("XLookupAction requires a lookup_value_column to be specified")
        if not self.return_column:
            raise NodeException("XLookupAction requires a return_column to be specified")
        if len(self.lookup_values) == 0:
            raise NodeException("XLookupAction requires a non-empty list of lookup_values to be specified")

    def _on_execute(self):
        data = self.get_parent_data()
        dataframe = DataUtils.dict_to_dataframe(data)
        required_columns = (self.lookup_column, self.return_column)
        missing_columns = [column for column in required_columns if column not in dataframe.columns]
        if missing_columns:
            raise NodeException(f"XLookupAction input is missing required columns: {missing_columns}")

        lookup_table = (
            dataframe.drop_duplicates(subset=self.lookup_column, keep="first")
            .set_index(self.lookup_column)[self.return_column]
        )
        lookup_values = pd.Series(self.lookup_values, dtype=object)
        found = lookup_values.isin(lookup_table.index)
        results = lookup_values.map(lookup_table)
        results.loc[~found] = self.not_found_value

        result_dataframe = pd.DataFrame({self.return_column: results})
        self.add_data(DataUtils.dataframe_to_dict(result_dataframe))
    