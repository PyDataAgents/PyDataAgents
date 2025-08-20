from typing import Union
import numpy as np
from loguru import logger

from ...services.plot.PlotlyElements import Mode, PlotType, Plotly, PlotlyDocument, Trace


class Plotlify:
    
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
        
        pdoc = PlotlyDocument(p)
        return pdoc
        
    @staticmethod
    def lines():
        pass
    
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