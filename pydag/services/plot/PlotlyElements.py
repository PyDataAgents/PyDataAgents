from enum import Enum
import json
import os
from pathlib import Path
from typing import Optional, Union, List
from bs4 import BeautifulSoup
from loguru import logger
import numpy as np

from pydag.utils.DataUtils import DataUtils

from ...utils.FileUtils import FileUtils

class AngleRef(str, Enum):
    PREVIOUS = "previous"
    UP = "up"
    
class Frame:
    def __init__(self,
                 x: Union[List[object], float],
                 y: Union[List[object], float],
                 z: Union[List[object], float]):
        # Normalize inputs: wrap scalars into lists
        self.x = self._to_list(x)
        self.y = self._to_list(y)
        self.z = self._to_list(z)

    def _to_list(self, value: Union[List[object], float]) -> List[object]:
        if isinstance(value, list):
            return value
        else:
            # wrap scalar into list
            return [value]
    
class AspectMode(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"
    INDEPENDENT = "independent"
    DATA = "data"
    CUBE = "cube"
    
class AspectRatio:
    def __init__(self):
        self.x = 1.0
        self.y = 1.0
        self.z = 1.0

    # Fluent setters
    def set_x(self, value):
        self.x = value
        return self

    def set_y(self, value):
        self.y = value
        return self

    def set_z(self, value):
        self.z = value
        return self

    # Getters
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def __repr__(self):
        return f"AspectRatio(x={self.x}, y={self.y}, z={self.z})"
    
class Axis:
    def __init__(self):
        self.range: Optional[List[float]] = None
        self.title: Optional[str] = None
        self.scaleanchor: Optional[str] = None
        self.scaleratio: int = 0
        self.autotick: bool = True
        self.zeroline: bool = True
        self.showline: bool = False
        self.showgrid: bool = True
        self.gridcolor: Optional[str] = None
        self.showticklabels: bool = True
        self.mirror: Optional[str] = None
        self.linecolor: Optional[str] = None

    # -------- Builder-style setters ----------
    def set_range(self, range_vals: List[float]) -> "Axis":
        self.range = range_vals
        return self

    def set_title(self, title: str) -> "Axis":
        self.title = title
        return self

    def set_autotick(self, autotick: bool) -> "Axis":
        self.autotick = autotick
        return self

    def set_zeroline(self, zeroline: bool) -> "Axis":
        self.zeroline = zeroline
        return self

    def set_showline(self, showline: bool) -> "Axis":
        self.showline = showline
        return self

    def set_showgrid(self, showgrid: bool) -> "Axis":
        self.showgrid = showgrid
        return self

    def set_gridcolor(self, gridcolor: str) -> "Axis":
        self.gridcolor = gridcolor
        return self

    def set_showticklabels(self, showticklabels: bool) -> "Axis":
        self.showticklabels = showticklabels
        return self

    def set_mirror(self, mirror: str) -> "Axis":
        self.mirror = mirror
        return self

    def set_linecolor(self, linecolor: str) -> "Axis":
        self.linecolor = linecolor
        return self

    def set_scaleanchor(self, scaleanchor: str) -> "Axis":
        self.scaleanchor = scaleanchor
        return self

    def set_scaleratio(self, scaleratio: int) -> "Axis":
        self.scaleratio = scaleratio
        return self
    
class Animation:
    def __init__(self, plot_id: str, trace_num: int):
        self.frames: List[Frame] = []
        self.plot_id = plot_id
        self.trace_num = trace_num

    def add(self, frame: Frame):
        self.frames.append(frame)

    def __str__(self) -> str:
        # Convert frames to strings (Frame.__str__ gives JSON)
        frames_str = "[" + ", ".join(str(frame) for frame in self.frames) + "]"
        sb = []
        sb.append(f"var traceNum = {self.trace_num};\n")
        sb.append(f"var animationData = {frames_str};\n")
        return "".join(sb)
    
class Color:
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, hex_color: str = None):
        if hex_color is not None:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) != 6:
                raise ValueError("Color string must be in HEX format (RRGGBB or #RRGGBB)")
            self.r = int(hex_color[0:2], 16)
            self.g = int(hex_color[2:4], 16)
            self.b = int(hex_color[4:6], 16)
        else:
            self.r = r
            self.g = g
            self.b = b

    def __str__(self):
        return f"rgb({self.r}, {self.g}, {self.b})"

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"


# Predefined constants (class attributes)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.GRAY = Color(128, 128, 128)
Color.ORANGE = Color(255, 150, 0)

class ColorBar:
    def __init__(self, x: int = 0, xanchor: str = None, side: str = None):
        self.x = x
        self.xanchor = xanchor
        self.side = side

    def set_x(self, x: int):
        """Fluent setter like in Java."""
        self.x = x
        return self

    def __repr__(self):
        return f"ColorBar(x={self.x}, xanchor={self.xanchor}, side={self.side})"
    
class DashType(str, Enum):
    DASH = "dash"
    DOT = "dot"
    DASHDOT = "dashdot"
    SOLID = "solid"

    def __str__(self):
        return self.value
    
class Domain:
    def __init__(self, x: Optional[List[float]] = None, y: Optional[List[float]] = None):
        self.x = x
        self.y = y

    # Optional: fluent setter methods
    def set_x(self, x: List[float]):
        self.x = x
        return self

    def set_y(self, y: List[float]):
        self.y = y
        return self

    def __repr__(self):
        return f"Domain(x={self.x}, y={self.y})"
    
class Grid:
    def __init__(self, rows: int = 1, columns: int = 1, pattern: str = "coupled"):
        self.rows = rows
        self.columns = columns
        self.pattern = pattern

    # Fluent setters
    def set_rows(self, rows: int):
        self.rows = rows
        return self

    def set_columns(self, columns: int):
        self.columns = columns
        return self

    def set_pattern(self, pattern: str):
        self.pattern = pattern
        return self

    # Getter methods (optional in Python)
    def get_rows(self):
        return self.rows

    def get_columns(self):
        return self.columns

    def get_pattern(self):
        return self.pattern

    def __repr__(self):
        return f"Grid(rows={self.rows}, columns={self.columns}, pattern='{self.pattern}')"

class TextFont:
    def __init__(self, family: str = None, size: int = 12, color: str = None):
        self.family = family
        self.size = size
        self.color = color

    # Getters
    def get_family(self):
        return self.family

    def get_size(self):
        return self.size

    def get_color(self):
        return self.color

    # Setters
    def set_family(self, family: str):
        self.family = family

    def set_size(self, size: int):
        self.size = size

    def set_color(self, color: str):
        self.color = color

    def __repr__(self):
        return f"TextFont(family={self.family}, size={self.size}, color={self.color})"

class Legend:
    def __init__(self):
        self.y = 0.0
        self.yref = None
        self.font = None

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def get_yref(self):
        return self.yref

    def set_yref(self, yref):
        self.yref = yref

    def get_font(self):
        if self.font is None:
            self.font = TextFont()
        return self.font

    def set_font(self, font):
        self.font = font

class LineShape(str, Enum):
    LINEAR = "linear"
    SPLINE = "spline"
    VHV = "vhv"
    HVH = "hvh"
    HV = "hv"
    VH = "vh"

    def __str__(self):
        return self.value
        
class Line:
    def __init__(self):
        self.dash = None
        self.width = 3
        self.shape = None
        self.color = None

    def get_dash(self):
        return self.dash

    def set_dash(self, dash_type):
        # expects dash_type to be an enum or object with __str__ defined
        self.dash = str(dash_type)
        return self

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width
        return self

    def get_shape(self):
        return self.shape

    def set_shape(self, line_shape):
        # expects line_shape to be an enum or object with __str__ defined
        self.shape = str(line_shape)
        return self

    def get_color(self):
        return self.color

    def set_color(self, color):
        # expects color to be an object with __str__ defined or a string
        self.color = str(color)
        return self
    
class Scene:
    def __init__(self):
        self.xaxis = None
        self.yaxis = None
        self.zaxis = None
        self.aspectmode = None
        self.aspectratio = None
        self.domain = None

    # X Axis
    def get_xaxis(self):
        if self.xaxis is None:
            self.xaxis = Axis()
        return self.xaxis

    def set_xaxis(self, xaxis):
        self.xaxis = xaxis
        return self

    # Y Axis
    def get_yaxis(self):
        if self.yaxis is None:
            self.yaxis = Axis()
        return self.yaxis

    def set_yaxis(self, yaxis):
        self.yaxis = yaxis
        return self

    # Z Axis
    def get_zaxis(self):
        if self.zaxis is None:
            self.zaxis = Axis()
        return self.zaxis

    def set_zaxis(self, zaxis):
        self.zaxis = zaxis
        return self

    # Aspect Ratio
    def aspect_ratio(self):
        if self.aspectratio is None:
            self.aspectratio = AspectRatio()
        return self.aspectratio

    def set_aspect_ratio(self, aspectratio):
        self.aspectratio = aspectratio
        return self

    # Aspect Mode
    def aspect_mode(self):
        return self.aspectmode

    def set_aspect_mode(self, aspectmode):
        self.aspectmode = str(aspectmode)
        return self

    # Domain (optional getter/setter if needed)
    def get_domain(self):
        return self.domain

    def set_domain(self, domain):
        self.domain = domain
        return self

    def __repr__(self):
        return (
            f"Scene(xaxis={self.xaxis}, yaxis={self.yaxis}, zaxis={self.zaxis}, "
            f"aspectmode={self.aspectmode}, aspectratio={self.aspectratio}, domain={self.domain})"
        )
        
class Title:
    def __init__(self):
        self.text = "Plotly"

    # Getter
    def get_text(self):
        return self.text

    # Setter
    def set_text(self, text):
        self.text = text
        return self  # optional, for fluent chaining

    def __repr__(self):
        return f"Title(text={self.text})"
    
class Margin:
    def __init__(self):
        self.l = 50
        self.r = 50
        self.b = 100
        self.t = 100
        self.pad = 4

    def get_l(self):
        return self.l

    def set_l(self, l):
        self.l = l

    def get_r(self):
        return self.r

    def set_r(self, r):
        self.r = r

    def get_b(self):
        return self.b

    def set_b(self, b):
        self.b = b

    def get_t(self):
        return self.t

    def set_t(self, t):
        self.t = t

    def get_pad(self):
        return self.pad

    def set_pad(self, pad):
        self.pad = pad

    def __repr__(self):
        return f"Margin(l={self.l}, r={self.r}, b={self.b}, t={self.t}, pad={self.pad})"

class Symbol(str, Enum):
    X = "x"
    CROSS = "cross"
    DIAMOND = "diamond"
    SQUARE = "square"
    TRIANGLE_UP = "triangle-up"
    TRIANGLE_DOWN = "triangle-down"
    ARROW_UP = "arrow-up"
    ARROW_UP_OPEN = "arrow-up-open"
    ARROW_DOWN = "arrow-down"
    ARROW_DOWN_OPEN = "arrow-down-open"
    ARROW_LEFT = "arrow-left"
    ARROW_LEFT_OPEN = "arrow-left-open"
    ARROW_RIGHT = "arrow-right"
    ARROW_RIGHT_OPEN = "arrow-right-open"
    ARROW_BAR_UP = "arrow-bar-up"
    ARROW_BAR_UP_OPEN = "arrow-bar-up-open"
    ARROW_BAR_DOWN = "arrow-bar-down"
    ARROW_BAR_DOWN_OPEN = "arrow-bar-down-open"
    ARROW_BAR_LEFT = "arrow-bar-left"
    ARROW_BAR_LEFT_OPEN = "arrow-bar-left-open"
    ARROW_BAR_RIGHT = "arrow-bar-right"
    ARROW_BAR_RIGHT_OPEN = "arrow-bar-right-open"
    ARROW = "arrow"
    ARROW_OPEN = "arrow-open"
    ARROW_WIDE = "arrow-wide"
    ARROW_WIDE_OPEN = "arrow-wide-open"

    def __str__(self) -> str:
        return self.value

class Marker:
    def __init__(self, size: int = 12, color: Union[str, List[float], None] = None, 
                 symbol: Optional[str] = None, angleref: AngleRef = None, 
                 line: Optional["Line"] = None):
        self.size = size
        self.color = color
        self.symbol = symbol
        self.angleref = str(angleref)
        self.line = line

    def get_size(self) -> int:
        return self.size

    # --- size ---
    def set_size(self, size: int) -> "Marker":
        self.size = size
        return self

    # --- color (can be string/enum or array) ---
    def set_color(self, value: Union["Color", List[float]]) -> "Marker":
        if isinstance(value, list):
            self.color = value
        else:
            self.color = str(value)
        return self

    def get_color(self) -> Union[str, List[float]]:
        return self.color

    # --- symbol ---
    def set_symbol(self, value: Union[str, Symbol]) -> "Marker":
        self.symbol = str(value)
        return self

    def get_symbol(self) -> str:
        return self.symbol

    # --- angleRef ---
    def set_angle_ref(self, angleref: AngleRef) -> "Marker":
        self.angleref = str(angleref)
        return self

    def get_angle_ref(self) -> str:
        return self.angleref

    # --- line ---
    def set_line(self, line: Line) -> "Marker":
        if line is None:
            if self.line is None:
                self.line = Line()
            return self.line
        self.line = line
        return self

class Mode(str, Enum):
    MARKERS = "markers"
    LINES = "lines"
    LINES_MARKERS = "lines+markers"
    LINES_MARKERS_TEXT = "lines+markers+text"
    MARKERS_TEXT = "markers+text"
    LINES_TEXT = "lines+text"

    def __str__(self) -> str:
        return self.value

class PlotType(str, Enum):
    SCATTER = "scatter"
    BAR = "bar"
    PIE = "pie"
    SCATTER3D = "scatter3d"
    SURFACE = "surface"
    MESH3D = "mesh3d"
    CONE = "cone"

    def __str__(self) -> str:
        return self.value
    
class TextPosition(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    TOP_LEFT = "top left"
    TOP_CENTER = "top center"
    TOP_RIGHT = "top right"
    MIDDLE_LEFT = "middle left"
    MIDDLE_CENTER = "middle center"
    MIDDLE_RIGHT = "middle right"

    def __str__(self) -> str:
        return self.value

class Trace:
    
    _TRACE_NUM = 0

    def __init__(self):
        Trace._TRACE_NUM += 1
        self.x: Union[list[object], list[float], list[int], np.ndarray] = None
        self.y: Union[list[object], list[float], list[int], np.ndarray] = None
        self.z: Union[list[object], list[float], list[int], np.ndarray] = None

        self.mode: Optional[str] = None
        self.type: Optional[str] = None
        self.name: str = f"trace{Trace._TRACE_NUM}"
        self.line: Optional[Line] = None
        self.text: Optional[List[str]] = None
        self.font: Optional[TextFont] = None
        self.textposition: Optional[str] = None
        self.marker: Optional[Marker] = None
        self.opacity: float = 1.0

        # cone-specific
        self.u: Union[list[object], list[float], list[int], np.ndarray] = None
        self.v: Union[list[object], list[float], list[int], np.ndarray] = None
        self.w: Union[list[object], list[float], list[int], np.ndarray] = None
        self.showscale: bool = False
        self.colorscale: Optional[List[object]] = None

        # subplot axes
        self.xaxis: Optional[str] = None
        self.yaxis: Optional[str] = None
        self.zaxis: Optional[str] = None

    # ---------------- DATA ----------------

    def set_x(self, x: Union[list[object], list[float], list[int], np.ndarray]):
        if isinstance(x, np.ndarray):
            self.x = x.tolist()
        else:
            self.x = x
        return self

    def set_y(self, y: Union[list[object], list[float], list[int], np.ndarray]):
        if isinstance(y, np.ndarray):
            self.y = y.tolist()
        else:
            self.y = y
        return self

    def set_z(self, z: Union[list[object], list[float], list[int], np.ndarray]):
        if isinstance(z, np.ndarray):
            self.z = z.tolist()
        else:
            self.z = z
        return self

    def set_u(self, u: Union[list[object], list[float], list[int], np.ndarray]):
        if isinstance(u, np.ndarray):
            self.u = u.tolist()
        else:
            self.u = u
        return self

    def set_v(self, v: Union[list[object], list[float], list[int], np.ndarray]):
        if isinstance(v, np.ndarray):
            self.v = v.tolist()
        else:
            self.v = v
        return self

    def set_w(self, w: Union[List[float], List[object]]):
        if isinstance(w, np.ndarray):
            self.w = w.tolist()
        else:
            self.w = w
        return self

    def set_mode(self, mode: Mode):
        self.mode = str(mode)
        return self

    def set_type(self, t: PlotType):
        self.type = str(t)
        return self

    def set_name(self, name: str):
        self.name = name
        return self

    def set_text(self, text: List[str]):
        self.text = text
        return self

    def set_font(self, font: TextFont = None):
        if font is None:
            if self.font is None:
                self.font = TextFont()
        else:
            self.font = font
        return self.font

    def set_text_position(self, pos: TextPosition):
        self.textposition = str(pos)
        return self

    def set_line(self, line: Line = None):
        if line is None:
            if self.line is None:
                self.line = Line()
        else:
            self.line = line
        return self.line

    def set_marker(self, marker: Marker = None):
        if marker is None:
            if self.marker is None:
                self.marker = Marker()
        else:
            self.marker = marker
        return self.marker

    def set_opacity(self, opacity: float):
        if not (0.0 <= opacity <= 1.0):
            raise ValueError("opacity must be between 0.0 and 1.0")
        self.opacity = opacity
        return self

    def set_colorscale(self, colorscale: List[object]):
        self.colorscale = colorscale
        return self

    def force_precision(self, precision: int):
        if self.x is not None:
            self.x = [round(self.x, precision) for xi in self.x]
        if self.y is not None:
            self.y = [round(self.y, precision) for yi in self.y]
        if self.z is not None:
            self.z = [round(self.z, precision) for zi in self.z]
        if self.u is not None:
            self.u = [round(self.u, precision) for ui in self.u]
        if self.v is not None:
            self.v = [round(self.v, precision) for vi in self.v]
        if self.z is not None:
            self.z = [round(self.z, precision) for zi in self.z]
        return self
    
    def to_dict(self) -> dict:
        return DataUtils.obj_to_dict(self, True)
    
class Layout:
    
    def __init__(self):
        self.scene : Scene = None
        self.xaxis : Axis = None
        self.yaxis : Axis = None
        self.zaxis : Axis = None
        self.height : int = 0
        self.width : int = 0
        self.legend = None
        self.showlegend = False
        self.title : Title = None
        self.grid : Grid = None
        self.margin : Margin = None
        self.autosize : bool = True
        self.plot_bgcolor = None
        self.paper_bgcolor = None

    def equal_axis(self):
        if self.yaxis is None:
            self.yaxis = Axis()
        self.yaxis.set_scaleanchor("x")
        self.yaxis.set_scaleratio(1)
        return self

    def equal_axis_3d(self):
        if self.scene is None:
            self.scene = Scene()
        self.scene.set_aspect_mode(AspectMode.DATA)
        return self

    def x_axis(self):
        if self.xaxis is None:
            self.xaxis = Axis()
        return self.xaxis

    def set_x_axis(self, xaxis):
        self.xaxis = xaxis
        return self

    def get_y_axis(self):
        if self.yaxis is None:
            self.yaxis = Axis()
        return self.yaxis

    def set_y_axis(self, yaxis):
        self.yaxis = yaxis
        return self

    def get_z_axis(self):
        if self.zaxis is None:
            self.zaxis = Axis()
        return self.zaxis

    def set_z_axis(self, zaxis):
        self.zaxis = zaxis
        return self

    def get_scene(self):
        if self.scene is None:
            self.scene = Scene()
        return self.scene

    def get_legend(self):
        return self.legend

    def set_legend(self, legend):
        self.legend = legend
        return self

    def get_title(self):
        if self.title is None:
            self.title = Title()
        return self.title

    def set_title(self, title):
        self.title = title
        return self

    def set_title_text(self, text):
        if self.title is None:
            self.title = Title()
        self.title.text(text)
        return self

    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height
        self.autosize = False
        return self

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width
        self.autosize = False
        return self

    def get_showlegend(self):
        return self.showlegend

    def set_showlegend(self, showlegend):
        self.showlegend = showlegend
        return self

    def get_grid(self):
        if self.grid is None:
            self.grid = Grid()
        return self.grid

    def set_grid(self, grid):
        self.grid = grid
        return self

    def get_margin(self):
        if self.margin is None:
            self.margin = Margin()
        return self.margin

    def set_margin(self, margin):
        self.margin = margin
        return self

    def get_autosize(self):
        return self.autosize

    def set_autosize(self, autosize):
        self.autosize = autosize
        return self

    def set_background_color(self, color):
        self.plot_bgcolor = color
        return self

    def get_background_color(self):
        return self.plot_bgcolor

    def set_paper_color(self, color):
        self.paper_bgcolor = color
        return self

    def get_paper_color(self):
        return self.paper_bgcolor

    def to_dict(self) -> dict:
       return DataUtils.obj_to_dict(self, True)
    
class Plotly:
    """
    Wrapper class for Plotly.js
    https://plotly.com/javascript/
    """

    _PLOTLY_NUM = 0

    def __init__(self, plot_id: Optional[str] = None):
        Plotly._PLOTLY_NUM += 1
        self.plot_id = plot_id if plot_id else f"plot{Plotly._PLOTLY_NUM}"
        self.data: List[Trace] = []
        self.layout: Optional[Layout] = None

    def to_script(self) -> str:
        """
        Returns a <script> block text to insert this Plotly figure into an HTML document.
        """
        if len(self.data) < 1:
            raise ValueError("Plotly must have at least one Trace")

        sb = []

        # div search
        sb.append(
            f"var plotDiv{Plotly._PLOTLY_NUM} = document.getElementById('{self.plot_id}');\n"
        )

        # traces
        trace_refs = []
        for i, t in enumerate(self.data, start=1):
            sb.append(f"\tvar trace{i} = {json.dumps(t.to_dict())};\n\n")
            trace_refs.append(f"trace{i}")

        sb.append(f"\tvar data = [{', '.join(trace_refs)}];\n\n")

        # layout
        if self.layout is not None:
            sb.append(f"\tvar layout = {json.dumps(self.layout.to_dict())};\n\n")
        else:
            sb.append("\tvar layout = {};\n\n")

        # final plot
        sb.append(
            f"\tPlotly.newPlot('{self.plot_id}', data, layout, {{responsive: true}});"
        )

        return "".join(sb)

    def trace(self, name: str) -> Trace:
        """
        Returns the Trace with given name.
        If none exists, creates a new one.
        """
        for t in self.data:
            if t.name == name:
                return t
        t = Trace().set_name(name)
        self.data.append(t)
        return t

    def set_trace(self, name: str, trace: Trace):
        """
        Adds or replaces a trace with the given name.
        """
        for i, tr in enumerate(self.data):
            if tr.name == name:
                self.data[i] = trace.set_name(name)
                return self
        self.data.append(trace.set_name(name))
        return self

    def get_traces(self) -> List[Trace]:
        return self.data

    def set_traces(self, traces: List[Trace]):
        self.data = traces

    def get_layout(self) -> Layout:
        if self.layout is None:
            self.layout = Layout()
        return self.layout

    def set_layout(self, layout: Layout):
        self.layout = layout

    def subplots(self):
        """
        Prepares traces for subplotting (x2, y2, z2, ...)
        Only works if a Grid is defined in Layout.
        """
        first = True
        i = 2
        for t in self.data:
            if first:
                first = False
            else:
                if t.x is not None:
                    t.xaxis = f"x{i}"
                if t.y is not None:
                    t.yaxis = f"y{i}"
                    t.xaxis = f"x{i}"
                if t.z is not None:
                    t.zaxis = f"z{i}"
                i += 1
        return self

    def get_plot_id(self) -> str:
        return self.plot_id
    
    def to_dict(self) -> dict:
        return DataUtils.obj_to_dict(self, True)
    
class PlotlyDocument:
    
    PLOTLY_TEMPLATE = "resources" + os.sep + "plotlify" + os.sep + "PLOTLY_TEMPLATE.html"
    PLOTLY_ANIMATION_TEMPLATE = "resources" + os.sep + "plotlify" + os.sep + "PLOTLY_ANIMATION_TEMPLATE.html"

    # default: no rounding (-1)
    PRECISION = -1

    def __init__(self, plotly=None):
        self.doc = None
        self.plotlys : List[Plotly] = []
        self.animation = None

        if plotly is not None:
            self.add_plotly(plotly)

    def add_plotly(self, plotly : Plotly):
        if plotly is None:
            raise ValueError("Specified plotly was None")
        self.plotlys.append(plotly)

    def _generate_doc(self):
        # load template
        if self.animation:
            with open(PlotlyDocument.PLOTLY_ANIMATION_TEMPLATE, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            with open(PlotlyDocument.PLOTLY_TEMPLATE, "r", encoding="utf-8") as f:
                html = f.read()

        if not html:
            raise IOError("Could not find Plotly HTML Template")

        self.doc = BeautifulSoup(html, "html.parser")

        for plotly in self.plotlys:
            # set doc title if available
            if plotly.get_layout().get_title():
                title_elem = self._get_element_by_tag(self.doc.head, "title", recursive=False)
                if title_elem:
                    title_elem.string = plotly.get_layout().get_title().get_text()

            # create div
            plot_div = self.doc.new_tag("div", id=plotly.get_plot_id(), style="width:100%; height:100%;")
            self.doc.body.append(plot_div)

            # enforce precision if required
            if self.PRECISION >= 0:
                for t in plotly.get_traces():
                    t.force_precision(self.PRECISION)

            # add script
            script_tag = self.doc.new_tag("script")
            script_tag.string = plotly.to_script()
            self.doc.body.append(script_tag)

        if self.animation:
            script_tag = self.doc.new_tag("script")
            script_tag.string = str(self.animation)
            # insert before last body element
            self.doc.body.insert(len(self.doc.body.contents) - 1, script_tag)

    @classmethod
    def from_html(cls, file_path):
        try:
            html_str = Path(file_path).read_text(encoding="utf-8")
            doc = BeautifulSoup(html_str, "html.parser")

            p_doc = cls()

            # get title
            title_tag = doc.head.find("title")
            title = title_tag.get_text() if title_tag else None

            # placeholder: parse plotly divs if needed
            # right now we just create one dummy Plotly
            plotly = Plotly()
            if title:
                plotly.get_layout().set_title(title)
            p_doc.add_plotly(plotly)

            return p_doc
        except IOError:
            logger.error(f"Could not read plotly file under {file_path}")
            return None

    def to_file(self, file_path="plotly.html", open_in_browser=True):
        self._generate_doc()
        Path(file_path).write_text(self.doc.prettify(), encoding="utf-8")

        if open_in_browser:
            FileUtils.open_file(file_path)

    def __str__(self):
        try:
            self._generate_doc()
            return str(self.doc)
        except IOError as e:
            logger.error(f"Could not generate {self.__class__.__name__}", exc_info=e)
            return None

    @staticmethod
    def _get_element_by_tag(elem, tag_name, recursive=True):
        """Find first child with tag_name"""
        if elem.name == tag_name:
            return elem
        if recursive:
            return elem.find(tag_name, recursive=True)
        else:
            return elem.find(tag_name, recursive=False)

    def get_plotlys(self):
        return self.plotlys

    def get_animation(self):
        return self.animation

    def set_animation(self, animation):
        self.animation = animation