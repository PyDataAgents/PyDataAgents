from dataclasses import dataclass, field

from ...utils.HTMLUtils import HTMLUtils
from ...utils.DataUtils import DataUtils

from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class HTMLTableAction(BufferNode, Action):
    """ This `BufferNode` creates a HTML Table string based on the parent data input to this `Node`.
    By default it outputs the HTML to a key named 'html' for child `Node`s to consume.
    """
    
    output_keys : list[str] = field(default_factory=lambda: ["html"])
    
    def _on_execute(self):
        data = self.get_parent_data()
        if isinstance(data, list):
            data = DataUtils.list_to_dict(data)  
        html_table = HTMLUtils.dict_to_htmltable(data)            
        new_data : dict = {self.output_keys[0]: html_table}
        self.add_data(new_data)