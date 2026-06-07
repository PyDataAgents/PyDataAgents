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
        self._ui_input_elements : dict[str, Element] = {}
        self._ui_output_elements : dict[str, Element] = {}
        self._ui_session_id_elem : Element = None
        self._ui_model_id_elem : Element = None
        
    def _render(self):
        self.create_header(f"Data Model {self._dms.model_name} - Dashboard")
        doc : str = self._dms.get_model_class().__doc__
        ui.label(doc)
        data_fields : Tuple[field] = fields(self._dms.get_model_class())
        self._create_input_form(self._dms.get_input_variables(), data_fields)
        self._create_output_form(self._dms.get_output_variables(), data_fields)
        ui.timer(0, self._init_model_session, once=True)
        
    def _create_input_form(self, input_variables: dict[str, str], datafields : Tuple[field]):
        with ui.column().classes('gap-2 w-full'):
            # 🔁 create inputs dynamically
            f : field
            for f in datafields:
                # check if field is in input variables
                n : str = f.name
                if n in input_variables:                    
                    t = f.type
                    d : str = f.metadata.get("description", "")
                    h : bool = f.metadata.get("hidden", False)
                    v : Any = getattr(self._dms.get_model_class(), n, None)
                    if not h:
                        if t is int:
                            self._ui_input_elements.update({n: ui.number(label=n, value=v, on_change=self._on_change).props(f"step=1 name={n}").tooltip(d)})
                        elif t is float:
                            self._ui_input_elements.update({n: ui.number(label=n, value=v, on_change=self._on_change).props(f"name={n}").tooltip(d)})
                        elif t is bool:
                            self._ui_input_elements.update({n: ui.switch(n, value=v, on_change=self._on_change).props(f"name={n}").tooltip(d)})
                        elif get_origin(t) is list:
                            self._ui_input_elements.update({n: ui.input_chips(label=n, value=v, new_value_mode="add", clearable=True, on_change=self._on_change).props(f"name={n}").tooltip(d)})
                        else:
                            self._ui_input_elements.update({n: ui.input(label=n, value=v, on_change=self._on_change).props(f"name={n}").tooltip(d)})


    def _create_output_form(self, output_variables: dict[str, str], datafields : Tuple[field]):
        with ui.column().classes('gap-2 w-full'):
            # 🔁 create inputs dynamically
            f : field
            for f in datafields:
                # check if field is in input variables
                n : str = f.name
                if n in output_variables:                    
                    t = f.type
                    d : str = f.metadata.get("description", "")
                    h : bool = f.metadata.get("hidden", False)
                    v : Any = getattr(self._dms.get_model_class(), n, None)
                    if not h:
                        if t is int:
                            self._ui_output_elements.update({n: ui.number(label=n, value=v).props(f"step=1 readonly name={n} input-class=bg-grey-2").tooltip(d)})
                        elif t is float:
                            self._ui_output_elements.update({n: ui.number(label=n, value=v).tooltip(d).props(f"readonly name={n} input-class=bg-grey-2")})
                        elif t is bool:
                            self._ui_output_elements.update({n: ui.switch(n, value=v).tooltip(d).props(f"readonly name={n} input-class=bg-grey-2")})
                        elif get_origin(t) is list:
                            self._ui_output_elements.update({n: ui.input_chips(label=n, value=v, new_value_mode="add", clearable=True).tooltip(d).props(f"readonly name={n} input-class=bg-grey-2")})
                        else:
                            self._ui_output_elements.update({n: ui.input(label=n, value=v).tooltip(d).props(f"readonly name={n} input-class=bg-grey-2")})

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
                if k in self._ui_input_elements:
                    self._ui_input_elements[k].set_value(v)
                if k in self._ui_output_elements:
                    self._ui_output_elements[k].set_value(v)
                            
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