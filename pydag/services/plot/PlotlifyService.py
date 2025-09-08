from typing import Union
import numpy as np
from loguru import logger

from ...buffers.Buffer import Buffer
from ...services.ServiceException import ServiceException
from ...services.Service import Service
from .PlotlyElements import Mode, PlotType, Plotly, PlotlyDocument, Trace


class PlotlifyService(Service):
    
    def start(self):
        super().start()
    
    def stop(self):
        super().stop()
    
    def create_plotly_doc(self, buffer_id, data : list[dict], layout : dict, plot_path : str) -> PlotlyDocument:
        """
            creates a plotly document from buffer data
        """
        if self.agent is not None:
            if buffer_id in self.agent.buffer_store:
                d = self.agent.get_buffer(buffer_id).data()
                # replace x, y, z props in provided data schema
                new_data = data.copy()
                for dic in new_data:
                    if "x" in dic:
                        x = dic["x"]
                        if x in d:
                            x_data = d[x]
                            dic["x"] = x_data
                        else:
                            raise ServiceException("key '" + x + "' is not present in this " + Buffer.cname() + " data")
                    if "y" in dic:
                        y = dic["y"]
                        if y in d:
                            y_data = d[y]
                            dic["y"] = y_data
                        else:
                            raise ServiceException("key '" + y + "' is not present in this " + Buffer.cname() + " data")
                    if "z" in dic:
                        z = dic["z"]
                        if z in d:
                            z_data = d[z]
                            dic["z"] = z_data
                        else:
                            raise ServiceException("key '" + z + "' is not present in this " + Buffer.cname() + " data")
                
                p = Plotly.from_dict(new_data, layout)
                pdoc = PlotlyDocument(p)
                pdoc.to_file(plot_path)
                return pdoc
            else:
                raise ServiceException("buffer with id '" + buffer_id + "' not found in buffer store")            
        else:
            raise ServiceException("no agent was assigned to this service")    
    
    @staticmethod
    def line(x : Union[list[object], list[float], list[int], np.ndarray] = None,
             y : Union[list[object], list[float], list[int], np.ndarray] = None, 
             z : Union[list[object], list[float], list[int], np.ndarray] = None,
             name : str = "trace1", title : str = "Plotly", x_label : str = "x", y_label : str = "y", z_label : str = "z") -> PlotlyDocument:
        """
            creates a line plot `PlotlyDocument`
        """
        if y is None:
            logger.error("No y data was specified, at least y data must be specified")
            return
        p = Plotly()
        p.get_layout().get_title().set_text(title)
        p.get_layout().get_scene().get_xaxis().set_title(x_label)
        p.get_layout().get_scene().get_yaxis().set_title(y_label)
        p.get_layout().get_scene().get_zaxis().set_title(z_label)
        
        t = Trace()
        t.set_x(x)
        t.set_y(y)
        t.set_z(z)
        t.set_name(name).set_mode(Mode.LINES)
        if z is None:
            t.set_type(PlotType.SCATTER3D)
        else:
            t.set_type(PlotType.SCATTER)
        
        p.get_traces().append(t)
        
        pdoc = PlotlyDocument(p)
        return pdoc
        
    @staticmethod
    def lines(x : Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]] = None,
             y : Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]] = None, 
             z : Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]] = None,
             names : list[str] = None, title : str = "Plotly", x_label : str = "x", y_label : str = "y", z_label : str = None) -> PlotlyDocument:
        """ creates a line plot of multiple lines as `PlotlyDocument`

        Args:
            x (Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]], optional): _description_. Defaults to None.
            y (Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]], optional): _description_. Defaults to None.
            z (Union[list[list[object]], list[list[float]], list[list[int]], list[np.ndarray]], optional): _description_. Defaults to None.
            name (str, optional): _description_. Defaults to "trace1".
            title (str, optional): _description_. Defaults to "Plotly".
            x_label (str, optional): _description_. Defaults to "x".
            y_label (str, optional): _description_. Defaults to "y".
            z_label (str, optional): _description_. Defaults to "z".

        Returns:
            PlotlyDocument: _description_
        """
        if y is None:
            logger.error("No y data was specified, at least y data must be specified")
            return
        p : Plotly = Plotly()
        p.get_layout().get_title().set_text(title)
        p.get_layout().get_scene().get_xaxis().set_title(x_label)
        p.get_layout().get_scene().get_yaxis().set_title(y_label)
        p.get_layout().get_scene().get_zaxis().set_title(z_label)
        
        for i in range(len(y)):
            t = Trace()
            t.set_mode(Mode.LINES)
            if x is not None:
                t.set_x(x[i])
            t.set_y(y[i])
            if z is not None:
                t.set_z(z[i])
            if names is not None:
                t.set_name(names[i])
            if z is not None:
                t.set_type(PlotType.SCATTER3D)
            else:
                t.set_type(PlotType.SCATTER)
            p.get_traces().append(t)
                
        pdoc = PlotlyDocument(p)
        return pdoc
    
    @staticmethod
    def scatter(x : Union[list[object], list[float], list[int], np.ndarray] = None,
             y : Union[list[object], list[float], list[int], np.ndarray] = None, 
             z : Union[list[object], list[float], list[int], np.ndarray] = None,
             name : str = "trace1", title : str = "Plotly", x_label : str = "x", y_label : str = "y", z_label : str = "z") -> PlotlyDocument:
        """
            creates a scatter plot `PlotlyDocument`
        """
        if y is None:
            logger.error("No y data was specified, at least y data must be specified")
            return
        p = Plotly()
        p.get_layout().get_title().set_text(title)
        p.get_layout().get_scene().get_xaxis().set_title(x_label)
        p.get_layout().get_scene().get_yaxis().set_title(y_label)
        p.get_layout().get_scene().get_zaxis().set_title(z_label)
        
        t = Trace()
        t.set_x(x)
        t.set_y(y)
        t.set_z(z)
        t.set_name(name).set_mode(Mode.MARKERS)
        if z is None:
            t.set_type(PlotType.SCATTER3D)
        else:
            t.set_type(PlotType.SCATTER)
            
        p.get_traces().append(t)
        
        pdoc = PlotlyDocument(p)
        return pdoc
    
    @staticmethod
    def scatter3D():
        pass
    
    @staticmethod
    def bar():
        pass
        
    @staticmethod
    def surface():
        pass
        
    @staticmethod
    def mesh3d():
        pass
    
    @staticmethod
    def annotation():
        pass    
    
    @staticmethod
    def arrow():
        pass
    
    @staticmethod
    def arrow3D():
        pass