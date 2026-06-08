from dataclasses import field, fields
from typing import Any, Tuple, get_origin

from nicegui import ui
from nicegui.element import Element


from ..Agent import Agent
from .UIElements import UIPage
from ...services.datamodel.DataModel import DataModel
from ...services.datamodel.DataModelService import DataModelService


class UIDataModelPage(UIPage):
    """ UI page for displaying `DataModelService`. """
    
    def __init__(self, agent : Agent, dms : DataModelService):
        super().__init__(agent)
        self.task_runner_id = id
        self.path = "/data_model"
        self._dms : DataModelService = dms
        self._ui_field_elements : dict[str, Element] = {}
        self._ui_session_id_elem : Element = None
        self._ui_model_id_elem : Element = None
        
    def _render(self):
        self.create_header(f"Data Model {self._dms.model_name} - Dashboard")
        doc : str = self._dms.get_model_class().__doc__
        ui.label(doc)
        self._create_fields(self._dms.get_input_variables())
        self._create_fields(self._dms.get_output_variables(), read_only=True)
        ui.timer(0, self._init_model_session, once=True)
        
    def _create_fields(self, variables: dict[str, str], read_only : bool = False):        
        data_fields : Tuple[field] = fields(self._dms.get_model_class())
        with ui.column().classes('gap-2 w-full'):
            # 🔁 create inputs dynamically
            f : field
            for f in data_fields:
                # check if field is in input variables
                n : str = f.name
                if n in variables:                    
                    t = f.type
                    d : str = f.metadata.get("description", "")
                    h : bool = f.metadata.get("hidden", False)
                    v : Any = getattr(self._dms.get_model_class(), n, None)
                    u : str = f.metadata.get("unit", None)
                    if not h:
                        elem : Element = None
                        if t is int:
                            elem = ui.number(label=n, value=v, on_change=self._on_change).props("step=1")
                        elif t is float:
                            elem = ui.number(label=n, value=v, on_change=self._on_change)
                        elif t is bool:
                            elem = ui.switch(n, value=v, on_change=self._on_change)
                        elif get_origin(t) is list:
                            elem = ui.input_chips(label=n, value=v, new_value_mode="add", clearable=True, on_change=self._on_change)
                        else:
                            elem = ui.input(label=n, value=v, on_change=self._on_change)
                        
                        elem.tooltip(d).props(f"name={n}")
                        if read_only:
                            elem.props("readonly input-class=bg-grey-2")
                        if u:
                            with elem.add_slot("append"):
                                ui.label(u).classes("text-gray-500 text-sm pb-3").style("height:100%; display: flex; align-items:flex-end;")
                        self._ui_field_elements.update({n: elem})

    async def _on_change(self, e):
        session_id = self._ui_session_id_elem.value
        model_id = self._ui_model_id_elem.value
        await self._dms.update(session_id, model_id, e.sender.props.get("name"), e.value)
        # update ui elements
        self._update_fields()
        with self._ui_session_id_elem:
            ui.notify(f"{DataModel.__name__} [{model_id}] updated in session [{session_id}]", color="green", position="bottom")
    
    def _update_fields(self):
        session_id = self._ui_session_id_elem.value
        model_id = self._ui_model_id_elem.value
        dm : DataModel = self._dms.get_data_model(session_id, model_id)        
        if dm:
            data : dict[str, Any] = dm.to_dict()
            for k, v in data.items():
                if k in self._ui_field_elements:
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