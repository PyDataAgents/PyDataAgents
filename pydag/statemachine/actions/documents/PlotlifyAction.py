from dataclasses import dataclass, field

from pydag.services.plot.PlotlyElements import Plotly, PlotlyDocument

from ....buffers.Buffer import Buffer
from ....statemachine.StatemachineException import StatemachineException
from ....statemachine.Action import Action
from ....statemachine.BufferNode import BufferNode


@dataclass
class PlotlifyAction(BufferNode, Action):
    
    plot_path : str = field(default=None, metadata={"description": "path for plotly html file"})
    data : list[dict] = field(default_factory=list[dict], metadata={"description": "plotly data dictionary with buffer keys for x,y,z data"})
    layout : dict = field(default_factory=dict, metadata={"description": "plotly layout dictionary"})
    
    def execute(self):
        d = self.buffer.data()
    
        # replace x, y, z props in 
        new_data = self.data.copy()
        for dic in new_data:
            if "x" in dic:
                x = dic["x"]
                if x in d:
                    x_data = d[x]
                    dic["x"] = x_data
                else:
                    raise StatemachineException("key '" + x + "' is not present in this " + Buffer.cname() + " data")
            if "y" in dic:
                y = dic["y"]
                if y in d:
                    y_data = d[y]
                    dic["y"] = y_data
                else:
                    raise StatemachineException("key '" + y + "' is not present in this " + Buffer.cname() + " data")
            if "z" in dic:
                z = dic["z"]
                if z in d:
                    z_data = d[z]
                    dic["z"] = z_data
                else:
                    raise StatemachineException("key '" + z + "' is not present in this " + Buffer.cname() + " data")
        
        p = Plotly.from_dict(new_data, self.layout)
        PlotlyDocument(p).to_file(self.plot_path)
    