from dataclasses import Field, fields
from pathlib import Path
from typing import Any, Tuple, get_origin

from nicegui import app, ui
from nicegui.element import Element
from nicegui.elements.image import Image

from pydag.agents.ui.UIException import UIException


from ..Agent import Agent
from .UIElements import UIPage
from ...services.datamodel.DataModel import DataModel
from ...services.datamodel.DataModelService import DataModelService


class UIDataModelPage(UIPage):
    """ UI page for displaying `DataModelService`. """
    
    def __init__(self, agent : Agent, dms : DataModelService, columns : int = 1):
        super().__init__(agent)
        self.task_runner_id = id
        self.path = "/data_model"
        self._dms : DataModelService = dms
        self._nc : int = columns
        self._columns : list[Element] = []
        self._ui_field_elements : dict[str, Element] = {}
        self._ui_session_id_elem : Element = None
        self._ui_model_id_elem : Element = None
        self._suspend_on_change: bool = False
        
    def _render(self):
        self.create_header(f"Data Model {self._dms.model_name} - Dashboard")
        doc : str = self._dms.get_model_class().__doc__
        # add global css 
        ui.add_head_html("""
            <style>
                .q-field__native {
                    font-size: 20px !important;
                }
                .q-field .q-field__label {
                    font-size: 20px !important;
                }
            </style>
        """)
        ui.label(doc)
        self._create_fields()
        ui.timer(0, self._init_model_session, once=True)
        
    def _create_fields(self):        
        data_fields : Tuple[Field] = fields(self._dms.get_model_class())        
        field : Field
        input_vars : dict[str, str] = self._dms.get_input_variables()
        output_vars : dict[str, str] = self._dms.get_output_variables()
        
        # go through all fields an search for design choices regarding number of columns and field groups       
        for col in self._columns:
            col.delete()
        self._columns.clear()
        # clear any previously stored field elements to avoid duplicate event handlers
        self._ui_field_elements.clear()
        with ui.row().classes("w-full"):
            for _ in range(0, self._nc):
                col : Element = ui.column()
                self._columns.append(col)
        
        divide_input_output : bool = False
        if self._nc == 2:
            cc : int = 0
            hc : int = 0
            for field in data_fields:
                c : int = field.metadata.get("ui_column", 0)
                h : bool = field.metadata.get("hidden", False)
                if c > cc:
                    cc = c
                if h:
                    hc += 1
            if cc == 0:
                divide_input_output = True
        
        # dictionary to store expansion groups
        group_elems : dict[str, Element] = dict()        
                        
        # create inputs dynamically
        f : int = 0        
        for field in data_fields:
            # check if field is in input variables
            n : str = field.name
            h : bool = False
            if n in input_vars or n in output_vars:                    
                t = field.type
                d : str = field.metadata.get("description", "")
                h = field.metadata.get("hidden", False)
                v : Any = getattr(self._dms.get_model_class(), n, None)
                u : str = field.metadata.get("unit", None)
                l : str = field.metadata.get("ui_label", None) 
                l = l if l is not None else n
                ut : str = field.metadata.get("ui_type", None)
                c : int = field.metadata.get("ui_column", 0)
                o : dict[str, Any] = field.metadata.get("ui_options", None)
                od : int = field.metadata.get("ui_order", 0)
                g : str = field.metadata.get("ui_group", None)
                if not h:
                    elem : Element = None                    
                    if g:
                        if g not in group_elems:
                            if divide_input_output:
                                if n in input_vars:
                                    with self._columns[0]:
                                        g_elem = ui.expansion(text = g, value = False)
                                        group_elems.update({g: g_elem})
                                else:
                                    with self._columns[1]:
                                        g_elem = ui.expansion(text = g, value = False)
                                        group_elems.update({g: g_elem})
                            else:
                                with self._columns[c]:
                                    g_elem = ui.expansion(text = g, value = False)
                                    group_elems.update({g: g_elem})
                        parent = group_elems[g]
                    else:
                        if divide_input_output:
                            if n in input_vars:
                                parent = self._columns[0]
                            else:
                                parent = self._columns[1]
                        else:
                            parent = self._columns[c]
                    with parent:
                        if ut:
                            match ut:
                                case "image":
                                    fname = Path(v).name
                                    app.add_static_file(local_file=v, url_path=f"assets/images/{fname}")
                                    elem = ui.image(source = v).classes('w-64')
                                case "table":
                                    pass
                                case "dropdown":
                                    pass
                                case "slider":
                                    pass
                                case "plot":
                                    pass
                                case _:
                                    raise UIException(f"unknown ui_type specified in {self.__class__.__name__}")
                        else:
                            if t is int:
                                elem = ui.number(label=l, value=v).props("step=1")
                            elif t is float:
                                elem = ui.number(label=l, value=v)
                            elif t is bool:
                                elem = ui.switch(l, value=v)
                            elif get_origin(t) is list:
                                elem = ui.input_chips(label=l, value=v, new_value_mode="add", clearable=True)
                            else:
                                elem = ui.input(label=l, value=v)
                        if n in input_vars:
                            elem.on("change", self._on_change)                        
                        elem.tooltip(d).props(f"name={n}")
                        if n in output_vars:
                            elem.props("readonly input-class=bg-grey-2")
                        if u:
                            with elem.add_slot("append"):
                                ui.label(u).classes("text-gray-500 text-sm pb-3").style("height:100%; display: flex; align-items:flex-end;")
                        self._ui_field_elements.update({n: elem})
                f += 1
                if h:
                    f -= 1

    async def _on_change(self, e):
        if self._suspend_on_change:
            return
        self._suspend_on_change = True
        try:
            session_id = self._ui_session_id_elem.value
            model_id = self._ui_model_id_elem.value
            await self._dms.update(session_id, model_id, e.sender.props.get("name"), e.sender.value)
            # update ui elements
            self._update_fields()
            with self._ui_session_id_elem:
                ui.notify(f"{DataModel.__name__} [{model_id}] updated in session [{session_id}]", color="green", position="bottom")
        except Exception as e:
            print(e)
        finally:
            self._suspend_on_change = False
        
    def _update_fields(self):
        session_id = self._ui_session_id_elem.value
        model_id = self._ui_model_id_elem.value
        dm : DataModel = self._dms.get_data_model(session_id, model_id)        
        if dm:
            data : dict[str, Any] = dm.to_dict()
            for k, v in data.items():
                if k in self._ui_field_elements:
                    if isinstance(self._ui_field_elements[k], Image):
                        if self._ui_field_elements[k].source != v:
                            self._ui_field_elements[k].set_source(v)
                    else:
                        if self._ui_field_elements[k].value != v:
                            self._ui_field_elements[k].set_value(v)
        
    async def _init_model_session(self):
        await ui.run_javascript("""
            if (!localStorage.session_id) {
                localStorage.session_id = crypto.randomUUID();
            }
            if (!localStorage.model_id) {
                localStorage.model_id = crypto.randomUUID();
            }
        """)
        session_id, model_id = await self._load_session_ids()
        if not session_id in self._dms.get_sessions():
            self._dms.create_session(session_id)
        with ui.footer().classes("bg-primary text-white"):
            with ui.row().classes("w-1/2 items-center gap-4"):
                self._ui_session_id_elem = ui.input(label="Session ID", value=session_id).props("readonly name=session_id input-class=text-white label-color=white").classes("flex-1 text-white").style("width: fit-content")
                self._ui_model_id_elem = ui.input(label="Model ID", value=model_id).props("readonly name=model_id input-class=text-white label-color=white").classes("flex-1 text-white")
        # update the fields with the current model data
        self._update_fields()

    async def _load_session_ids(self) -> Tuple[str, str]:
        session_id = await ui.run_javascript("localStorage.session_id")
        model_id = await ui.run_javascript("localStorage.model_id")
        return session_id, model_id