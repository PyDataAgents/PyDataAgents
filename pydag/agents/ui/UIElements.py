from __future__ import annotations
from abc import abstractmethod
import asyncio
from collections import deque
import copy
import enum
from typing import TYPE_CHECKING, Any
from nicegui import ui
from nicegui.element import Element
import plotly.graph_objs as go


from ...utils.DataUtils import DataUtils
from ..AgentConfig import AgentConfig
from ..AgentElement import AgentElement
from ..AgentStates import AgentElementState, ServiceState, BufferState, NodeState
from ...buffers.TimedBuffer import TimedBuffer
from ...buffers.Buffer import Buffer

if TYPE_CHECKING:
    from ..Agent import Agent

class UIType(str, enum.Enum):
    PLOT = "PLOT"
    TABLE = "TABLE"
    ITABLE = "ITABLE" # interactive table
    INPUT = "INPUT"
    GAUGE = "GAUGE"
    STAT = "STAT"
    BUTTON = "BUTTON"

def determine_ui_type(buffer : Buffer) -> UIType:
    """ checks the Buffer for the corresponding/probable UIType """
    # TODO
    
def determine_samples(buffer : Buffer) -> int:
    """ defines the number of samples to retrieve for a `BufferComponent`"""
    # TODO

class UIPage():
    """ Base Page class to build nicegui pages """
    
    path : str = "/"
    with_nav_bar : bool = True
    
    def __init__(self, agent : Agent, refresh_interval : int = 1.0):
        self._agent : Agent = agent
        self._ui_components : deque[UIComponent] = deque()
        self._refresh_interval : int = refresh_interval
        self._timer : ui.timer = None
    
    def register(self):
        
        @ui.page(self.path)
        def page():
            self._ui_components.clear()
            self._render()
            # check all ui components if timer is required
            requires_update : bool = False
            for component in self._ui_components:
                if component.requires_update:
                    requires_update = True
                    break                    
            if requires_update:
                self._timer = ui.timer(self._refresh_interval, lambda: [
                    component.update() for component in self._ui_components if component.requires_update 
                ])
    
    @abstractmethod
    def _render(self):
        """ page specific ui logic """
        
    def add_ui_component(self, component : UIComponent):
        """ adds the ui element to this page's ui element list """
        self._ui_components.append(component)
        
    def remove_ui_component(self, i : int):
        self._ui_components.rotate(-i)
        self._ui_components.popleft()
        self._ui_components.rotate(i)
        
    def get_ui_components(self) -> deque[UIComponent]:
        return self._ui_components
    
    def get_agent(self) -> Agent:
        return self._agent
    
    def create_header(self, title : str):
        """ creates a standard header with title and home link """
        with ui.header().classes('bg-primary text-white'):
            ui.label(f"{title}").classes("font-bold text-lg")
            ui.space()
            with ui.link(target="/").classes("flex items-center gap-2 text-white"):
                ui.icon("home").classes("text-xl")
   
class UIHomePage(UIPage):
    """ Main/Home Page with navigation cards for other UI Pages """
    
    path : str = "/"
    
    def _render(self):
        self.create_header("UI Home - Dashboard")
        with ui.grid(columns=4).classes("w-full gap-2"):
            for page in self._agent.get_ui_pages():
                link = page.path
                title = page.__class__.__name__
                desc = page.__doc__
                with ui.card().classes('p-4 cursor-pointer'):
                    ui.link(title, target=link)
                    if desc:
                        ui.label(desc).classes("text-sm text-gray-500")

class UIComponent():
    """ Base UI Component class """ 
    
    requires_update : bool = True  # shows the internal pages timer, that this element requires an update each iteration
    
    def __init__(self, page : UIPage):
        self._page : UIPage = page
        self._elements : deque[Element] = deque()
    
    @abstractmethod
    def update(self):
        """ update routine that is called from ui timer each interval """
        
    def add_element(self, element : Element):
        """ adds a new element to component """
        self._elements.append(element)
        
    def delete(self):
        """ deletes the component and all its respective elements and references """
        for elem in self._elements:
            elem.delete()
        # TODO
        # deletion of component and its references in update routine required

class BufferComponent(UIComponent):
    """ Abstract `Buffer` `UIComponent`

    Args:
        UIComponent (_type_): _description_
    """
       
    def __init__(self, page : UIPage, buffer : Buffer, input_keys : list[str] = None, n : int = 0):
        super().__init__(page)
        self._buffer : Buffer = buffer
        self._input_keys : list[str] = input_keys
        self._n : int = n
        
    def get_data(self) -> dict[str, list[Any]]:
        """ retrieves the data based on specified input_keys and n samples from connected `Buffer`"""
        if self._input_keys:
            data = self._buffer.data(n=self._n, persistent=True)
            new_data = {}
            for k in self._input_keys:
                if k in data:
                    new_data[k] = data[k]
            return new_data
        else:
            data = self._buffer.data(n=self._n, persistent=True)
            return data

class PlotCard(BufferComponent):
        
    def __init__(self, page : UIPage, buffer : Buffer, input_keys : list[str] = None, n : int = 0):
        super().__init__(page, buffer, input_keys, n)
        self._fig = go.Figure()
        if isinstance(buffer, TimedBuffer):
            self._fig.add_trace(go.Scatter(x=[], y=[], mode='lines'))
        else:
            self._fig.add_trace(go.Scatter(y=[], mode='lines'))        
        card = ui.card()
        self.add_element(card)
        with card:
            self._expansion = ui.expansion("Plot " + buffer.id)
            with self._expansion:
                self._ui_plot = ui.plotly(self._fig)
                
    def update(self):
        if not self._expansion.value:
            return
        data = self.get_data()
        n = len(data)
        if n > 0:
            if n == 1:
                y = next(iter(data.values()))
                self._fig.data[0].y = y
            else:
                if n == 2 and issubclass(self._buffer.__class__, TimedBuffer):        
                    it = iter(data.values())
                    x = next(it)
                    y = next(it)
                    self._fig.data[0].x = x
                    self._fig.data[0].y = y
                else:
                    t = len(self._fig.data)
                    if t != n:
                        # Adjust the number of traces in the figure
                        while len(self._fig.data) < n:
                            self._fig.add_trace(go.Scatter(y=[], mode='lines'))
                        while len(self._fig.data) > n:
                            self._fig.pop(-1)
                    it = iter(data.values())           
                    for i in range(0, n): 
                        y = next(it) 
                        self._fig.data[i].y = y
            self._ui_plot.update()


ROW_KEY = "__row_id__"

class BufferTable(BufferComponent):
    """UI element that renders a buffer as a filterable and sortable table."""

    def __init__(self, page : UIPage, buffer : Buffer, input_keys : list[str] = None, n : int = 0):
        super().__init__(page, buffer, input_keys, n)
        self._columns : list[dict] = []
        card = ui.card()
        self.add_element(card)
        with card.classes("w-full"):
            self._expansion = ui.expansion("Table " + buffer.id)
            with self._expansion:
                self._filter = ui.input(placeholder="Filter").props("clearable dense outlined").classes("w-full")
                self._ui_table = ui.table(
                    rows=[],
                    columns=[],
                    row_key=ROW_KEY,
                    pagination={"rowsPerPage": 25},
                ).classes("w-full")
                self._ui_table.bind_filter_from(self._filter, "value")

    def update(self):
        if not self._expansion.value:
            return
        data = self.get_data()
        rows, columns = self._table_data(data)
        if columns != self._columns:
            self._columns = columns
            self._ui_table.columns = columns
        self._ui_table.rows = rows
        self._ui_table.update()

    def _table_data(self, data : dict) -> tuple[list[dict], list[dict]]:
        if len(data) == 0:
            return [], []
        row_count = self._row_count(data)
        columns = [
            {"name": ROW_KEY, "label": "#", "field": ROW_KEY, "sortable": True},
            *[
                {"name": key, "label": str(key), "field": key, "sortable": True}
                for key in data.keys()
            ],
        ]
        rows = []
        for i in range(row_count):
            row = {ROW_KEY: i}
            for key, value in data.items():
                row[key] = self._cell_at(value, i)
            rows.append(row)
        return rows, columns

    def _row_count(self, data : dict) -> int:
        lengths = [len(value) for value in data.values() if self._is_sequence(value)]
        return max(lengths) if lengths else 1

    def _cell_at(self, value : Any, index : int) -> Any:
        if self._is_sequence(value):
            if index >= len(value):
                return None
            value = value[index]
        return self._format_cell(value)

    def _is_sequence(self, value : Any) -> bool:
        return hasattr(value, "__len__") and not isinstance(value, (str, bytes, dict))

    def _format_cell(self, value : Any) -> Any:
        if isinstance(value, (list, tuple, set, dict)):
            return str(value)
        if hasattr(value, "item"):
            return value.item()
        return value

class AgentElementConfigForm(UIComponent):
    """ UI Element that renders a submit form for changing `AgentElement` config properties """
    
    def __init__(self, page : UIPage, agent_element : AgentElement):
        super().__init__(page)      
        self._agent_element = agent_element
        self._card : Element = ui.card().classes("w-full m-1")
        self._id_label : Element = None
        self._state_label : Element = None
        self._buffersize_label : Element = None
        self.add_element(self._card)
        self._render_form()
            
                    
    def _render_form(self, expanded : bool = False):
        config_options = self._agent_element.config_options(True)
        if len(config_options) > 0:
            id = config_options[AgentConfig.ID]
            id_tt = id[AgentConfig.DESCRIPTION]
            t = config_options[AgentConfig.TYPE]
            t_tt = t[AgentConfig.DESCRIPTION]
            type_short = t[AgentConfig.VALUE].split(".")[-1]
            del config_options[AgentConfig.ID]
            del config_options[AgentConfig.TYPE]
            ui_inputs = {}
            self._card.clear()
            with self._card:
                expansion = ui.expansion().classes("w-full font-bold")
                expansion.value = expanded
                with expansion:
                    with expansion.add_slot("header"):
                        with ui.row().classes("items-center justify-between w-full p-1"):                            
                            doc : str = self._agent_element.__doc__
                            self._id_label = ui.label(f"{type_short} - {id[AgentConfig.VALUE]}").tooltip(doc)
                            if isinstance(self._agent_element, Buffer):
                                self._buffersize_label = ui.label(f"{self._agent_element.size()}/{self._agent_element.capacity}")
                            self._state_label = ui.label(self._agent_element.get_state())
                            self._style_state_label()                            
                    with ui.grid(columns=1).classes("w-full"):
                        ui_inputs[AgentConfig.ID] = ui.input(label=AgentConfig.ID, value=id[AgentConfig.VALUE]).tooltip(id_tt)
                        i : Element = ui.input(label=AgentConfig.TYPE, value=t[AgentConfig.VALUE]).tooltip(t_tt)
                        i.enabled = False
                        ui_inputs[AgentConfig.TYPE] = i
                        for config_option, config_value in config_options.items():
                            value = config_value[AgentConfig.VALUE]
                            description = config_value[AgentConfig.DESCRIPTION]
                            if isinstance(value, bool):
                                cb : Element = ui.checkbox(config_option).tooltip(description).classes("text-sm text-gray-500 font-normal")
                                cb.value = value
                                ui_inputs[config_option] = cb
                            elif isinstance(value, int):
                                ui_inputs[config_option] = ui.number(label=config_option, value=value).tooltip(description)
                            elif isinstance(value, float):
                                ui_inputs[config_option] = ui.number(label=config_option, value=value).tooltip(description)
                            elif isinstance(value, list):
                                ui_inputs[config_option] = ui.input_chips(label=config_option, value=value, new_value_mode="add", clearable=True).tooltip(description)
                            elif isinstance(value, dict):
                                if AgentConfig.TYPE in value:
                                    nested_agent_element : AgentElement = getattr(self._agent_element, config_option)
                                    ui.label(config_option).classes("text-sm text-gray-500 font-normal").tooltip(description)                                        
                                    if isinstance(nested_agent_element, AgentElement):
                                        ui_inputs[config_option] = AgentElementConfigForm(self._page, nested_agent_element)
                                    else:
                                        ui_inputs[config_option] = value
                                else:    
                                    ui_inputs[config_option] = value                                                                
                            else:
                                ui_inputs[config_option] = ui.input(label=config_option, value=value).tooltip(description)
                    
                    def on_submit():
                        data = {}
                        for k, e in ui_inputs.items():
                            #print(f"{k}: {type(e)}")
                            if isinstance(e, AgentElementConfigForm):
                                data[k] = e._agent_element.config_options()
                            elif isinstance(e, dict):
                                data[k] = e
                            else:
                                data[k] = e.value
                        self._handle_submit(data)
                    
                    ui.button('Submit', on_click=on_submit)
                    
    def _handle_submit(self, data : dict[str, Any]):
        #print(data)
        ui.notify(data, position="bottom", type="positive")
        self._page.get_agent().edit_element(self._agent_element.id, data)
        self._render_form(expanded=True)
        
    def update(self):
        self._state_label.text = self._agent_element.get_state()
        self._style_state_label()
        ts : str = self._agent_element.type.split(".")[-1]
        self._id_label.text = f"{ts} - {self._agent_element.id}"
        if isinstance(self._agent_element, Buffer):                                
            self._buffersize_label.text = f"{self._agent_element.size()}/{self._agent_element.capacity}"
          
    def _style_state_label(self):
        state = self._agent_element.get_state()
        match state:
            case AgentElementState.INSTALLED:
                self._state_label.classes('bg-gray-500 text-white p-2 rounded')
            case AgentElementState.UNINSTALLED:
                self._state_label.classes('bg-yellow-500 text-black p-2 rounded')
            case AgentElementState.ERROR:
                self._state_label.classes('bg-red-500 text-white p-2 rounded')
            case ServiceState.RUNNING:
                self._state_label.classes('bg-green-500 text-white p-2 rounded')
            case BufferState.STORING:
                self._state_label.classes('bg-green-500 text-white p-2 rounded')
            case BufferState.RETRIEVING:
                self._state_label.classes('bg-blue-500 text-white p-2 rounded')
            case NodeState.EXECUTING:
                self._state_label.classes('bg-green-500 text-white p-2 rounded')
        
    
class TrafficLight(BufferComponent):
    """ UI element that renders a boolean `Buffer` into a traffic light in red and green

    Args:
        UIComponent (_type_): _description_
    """
    
    def __init__(self, page : UIPage, buffer : Buffer, input_keys : list[str] = None, n : int = 1):
        super().__init__(page, buffer, input_keys, n)
        self._icon = ui.icon('circle').classes('text-4xl')
        self.add_element(self._icon)
        
    def update(self):
        data = self.get_data()
        if len(data) > 0:
            li = next(iter(data.values()))
            if len(li) > 0:
                value = bool(li[0])
                if value:
                    self._icon.classes(replace='text-4xl text-green-500')
                else:
                    self._icon.classes(replace='text-4xl text-red-500')
                
class EditableTable(ui.element):
    """
    Editable dictionary table component.

    Example:

        table = EditableTable(
            columns={
                "name": "Name",
                "age": "Age",
                "city": "City",
            },
            data=[
                {"name": "Alice", "age": 30, "city": "Berlin"},
                {"name": "Bob", "age": 25, "city": "Munich"},
            ]
        )

        table.on_change(lambda data: print(data))

    """

    def __init__(self, columns: dict[str, str], data: list[dict[str, Any]] | None = None):
        super().__init__("div")
        self.columns = columns
        self.value: list[dict[str, Any]] = []
        self._change_handler = None
        if data:
            self.set_value(data)
        self._render()

    def set_value(self, data: list[dict[str, Any]]):
        """
        Replace table contents.
        """
        for row in data:
            if set(row.keys()) != set(self.columns.keys()):
                raise ValueError("Data keys do not match columns")

        self.value = copy.deepcopy(data)
        self._render()

    def get_value(self) -> list[dict[str, Any]]:
        """
        Return a copy of current data.
        """
        return copy.deepcopy(self.value)

    def on_change(self, handler):
        """
        Register callback:

            handler(data)

        where data is the complete table.
        """
        self._change_handler = handler
        return self
    
    def _emit_change(self):
        if self._change_handler:
            result = self._change_handler(self.get_value())
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)

    def _render(self):
        self.clear()
        grid = (" ".join(["1fr"] * len(self.columns)) + " 50px")
        with self:
            # header
            with ui.element("div").classes("w-full grid gap-0 bg-grey-3 p-0 font-bold").style(f"grid-template-columns:{grid}"):
                for label in self.columns.values():
                    ui.label(label).classes("px-3 py-2 border border-gray-300")
                ui.label("#").classes("px-3 py-2 border border-gray-300")

            # rows
            for row_index, row in enumerate(self.value):

                with ui.element("div").classes("w-full grid gap-0 items-stretch").style(f"grid-template-columns:{grid}"):
                    for column in self.columns:
                        inp = ui.input(value=row.get(column, "")).classes("w-full border border-gray-300 px-3 py-2").props("outlined=False")

                        def update(e=None, r=row_index, c=column, widget=inp):
                            self.value[r][c] = DataUtils.force_numeric(widget.value)
                            self._emit_change()

                        inp.on("change", update)

                    ui.button(icon="delete", color="negative", on_click=lambda r=row_index: self._delete_row(r)).props("flat").classes("w-full h-full border border-gray-300 rounded-none flex items-center justify-center")

            ui.button("Add row", icon="add", on_click=self._add_row).classes("mt-2")


    def _add_row(self):
        self.value.append(
            {
                column: ""
                for column in self.columns
            }
        )

        self._render()
        self._emit_change()


    def _delete_row(self, index: int):
        if 0 <= index < len(self.value):
            self.value.pop(index)

        self._render()
        self._emit_change()