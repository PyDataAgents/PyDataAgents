from dataclasses import dataclass, field

from pydag.services.datamodel.DataModel import DataModel

@dataclass
class SelectDataModel(DataModel):
    """ Test Select DataModel """
    
    a : int = field(default=0, metadata={"description": "number field", "ui_label": "selector"})
    b : str = field(default="", metadata={"description": "dropdown field", "ui_type": "select", "ui_options": "@select_options"})
    c : str = field(default=None, metadata={"description": "display field", "ui_label": "display field"})
    select_options : list = field(default_factory=list, metadata={"description": "computed select options field", "hidden": True})
    
    def compute_select_options(self):
        options : list = []
        match self.a:
            case 0:
                options = ["Default", "Special"]
            case 1:
                options = ["1", "2", "3"]
            case 2:
                options = ["Apple", "Banana", "Pear"]
            case _:
                options = ["No Options"]
            
        self.select_options = options
    
    def compute_c(self):
        self.c = self.b