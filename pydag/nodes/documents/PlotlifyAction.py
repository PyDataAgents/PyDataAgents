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
    open_in_browser : bool = field(default=True, metadata={"description": "specifies whether to open the plotly file in browser after creation"})
    auto_refresh : int = field(default=0, metadata={"description": "if an interval greater than 0s is specified, then an meta-tag for page auto refresh is added to html"})
    colors : list[str] = field(default=None, metadata={"description": "lets you specify the colors to use from, when creating traces"})
    
    def _on_install(self, agent : Agent = None):
        if self._buffer is None:
            if agent is not None:
                buf = agent.get_buffer(self.buffer_id)
                if buf:
                    self._buffer = buf
        
    def _on_execute(self):
        if len(self.data) == 0:
            d = self.get_parent_data()
            new_data = []
            i = 0
            for k, v in d.items():
                trace = {}
                trace["y"] = v
                trace["name"] = k
                if self.colors is not None:
                    if len(d) <= len(self.colors):
                        trace["line"] = {"color": self.colors[i]}
                new_data.append(trace)
                i += 1
        else:
            new_data = self.data.copy()
            dlist : list[dict] = []
            if self._buffer is None:
                for parent in self._parents:
                    if isinstance(parent, BufferNode):
                        d = parent.get_buffer().data(n=self.n, persistent=self.persistent)
                        dlist.append(d)
            else:
                d = self._buffer.data(n=self.n, persistent=self.persistent)
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
                i = 0
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
                        if self.colors is not None:
                            if len(dlist) <= len(self.colors):
                                dic["line"] = {"color": self.colors[i]}
                    i += 1
                
                if not x_ok or not y_ok or not z_ok:
                    raise NodeException("any of the specified x, y, z mappings could not be found in the buffer data")
                
                if x_count > 1 or y_count > 1 or z_count > 1:
                    raise NodeException(" ")
            else:
                raise NodeException(f"no data was provided in {self.cname()} {Buffer.cname()}")

        p : Plotly = Plotly.from_dict(new_data, self.layout)
        pdoc : PlotlyDocument = PlotlyDocument(p)
        pdoc.generate_doc()
        if self.auto_refresh > 0:
            pdoc.auto_refresh(self.auto_refresh)
        pdoc.to_file(self.plot_path, open_in_browser=self.open_in_browser)