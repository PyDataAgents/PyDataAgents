from ast import List
from enum import Enum
import json
from typing import Optional, Union

class Plotly:
    pass
    

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
        self.text = None

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