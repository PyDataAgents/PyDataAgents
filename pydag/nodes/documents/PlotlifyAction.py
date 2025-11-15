from dataclasses import dataclass, field

from ...agents.Agent import Agent
from ...services.plot.PlotlyElements import Plotly, PlotlyDocument
from ...buffers.Buffer import Buffer
from ..Action import Action
from ..BufferNode import BufferNode
from ..NodeException import NodeException


@dataclass
class PlotlifyAction(BufferNode, Action):
    """ `Action` that generates a plotly file based on the data and layout specified and extracted from the specified buffer or its parents `Buffer`s.
    """
    
    plot_path : str = field(default=None, metadata={"description": "path for plotly html file"})
    data : list[dict] = field(default_factory=list[dict], metadata={"description": "plotly data dictionary with buffer keys for x,y,z data"})
    layout : dict = field(default_factory=dict, metadata={"description": "plotly layout dictionary"})
    
    def install(self, agent : Agent = None):
        Action.install(self, agent)
        if self.buffer is None:
            if agent is not None:
                if self.buffer_id in agent.buffer_store:
                    self.buffer = agent.buffer_store[self.buffer_id]
        
    def execute(self):
        new_data = self.data.copy()
        dlist : list[dict] = []
        if self.buffer is None:
            new_data = self.data.copy()
            for parent in self.parents:
                if isinstance(parent, BufferNode):
                    d = parent.buffer.data(n=self.n, persistent=self.persistent)
                    dlist.append(d)
        else:
            d = self.buffer.data(n=self.n, persistent=self.persistent)
            dlist.append(d)
        if len(dlist) > 0:
            first_x : bool = True
            first_y : bool = True
            first_z : bool = True
            x_ok : bool = True
            y_ok : bool = False
            z_ok : bool = True
            x_count : int = 0
            y_count : int = 0
            z_count : int = 0
            for d in dlist:
                # replace x, y, z props in 
                for dic in new_data:
                    if "x" in dic:
                        if first_x:
                            x_ok = False
                            first_x = False
                        x = dic["x"]
                        if x in d:
                            x_data = d[x]
                            dic["x"] = x_data
                            x_ok = True
                            x_count += x_count                            
                        else:
                            if len(dlist) == 1:
                                raise NodeException("key '" + x + "' is not present in this " + Buffer.cname() + " data")
                    if "y" in dic:
                        if first_y:
                            y_ok = False
                            first_y = False
                        y = dic["y"]
                        if y in d:
                            y_data = d[y]
                            dic["y"] = y_data
                            y_ok = True
                            y_count += y_count
                        else:
                            if len(dlist) == 1:
                                raise NodeException("key '" + y + "' is not present in this " + Buffer.cname() + " data")
                    if "z" in dic:
                        if first_z:
                            z_ok = False
                            first_z = False                        
                        z = dic["z"]
                        if z in d:
                            z_data = d[z]
                            dic["z"] = z_data
                            z_ok = True
                            z_count += z_count
                        else:
                            if len(dlist) == 1:
                                raise NodeException("key '" + z + "' is not present in this " + Buffer.cname() + " data")
            
            if not x_ok or not y_ok or not z_ok:
                raise NodeException("any of the specified x, y, z mappings could not be found in the buffer data")
            
            if x_count > 1 or y_count > 1 or z_count > 1:
                raise NodeException(" ")
            
            p = Plotly.from_dict(new_data, self.layout)
            PlotlyDocument(p).to_file(self.plot_path)
        else:
            raise NodeException(f"no data was provided in {self.cname()} {Buffer.cname()}")
    