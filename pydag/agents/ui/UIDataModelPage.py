from dataclasses import field, fields
from typing import Any, Tuple, get_origin

from nicegui import ui

from ..Agent import Agent
from .UIElements import UIPage
from ...services.datamodel.DataModelService import DataModelService


class UIDataModelPage(UIPage):
    """ UI page for displaying `DataModelService`. """
    
    def __init__(self, agent : Agent, dms : DataModelService):
        super().__init__(agent)
        self.task_runner_id = id
        self.path = "/data_model"
        self._dms : DataModelService = dms
        
    def _render(self):
        self.create_header(f"Data Model {self._dms.model_name} - Dashboard")
        doc : str = self._dms.get_model_class().__doc__
        ui.label(doc)
        data_fields : Tuple[field] = fields(self._dms.get_model_class())
        self._create_input_form(self._dms.get_input_variables(), data_fields)
        self._create_output_form(self._dms.get_output_variables(), data_fields)
        ui.timer(0, self._create_session_ids, once=True)
        
    def _create_input_form(self, input_variables: dict[str, str], datafields : Tuple[field]):
        inputs = {}
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
                            inputs[n] = ui.number(label=n, value=v).props(f"step=1 name={n}").tooltip(d)
                        elif t is float:
                            inputs[n] = ui.number(label=n, value=v).props(f"name={n}").tooltip(d)
                        elif t is bool:
                            inputs[n] = ui.switch(n, value=v).props(f"name={n}").tooltip(d)
                        elif get_origin(t) is list:
                            inputs[n] = ui.input_chips(label=n, value=v, new_value_mode="add", clearable=True).props(f"name={n}").tooltip(d)
                        else:
                            inputs[n] = ui.input(label=n, value=v).props(f"name={n}").tooltip(d)


    def _create_output_form(self, output_variables: dict[str, str], datafields : Tuple[field]):
        outputs = {}
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
                            outputs[n] = ui.number(label=n, value=v).props(f"step=1 readonly name={n}").tooltip(d)
                        elif t is float:
                            outputs[n] = ui.number(label=n, value=v).tooltip(d).props(f"readonly name={n}")
                        elif t is bool:
                            outputs[n] = ui.switch(n, value=v).tooltip(d).props(f"readonly name={n}")
                        elif get_origin(t) is list:
                            outputs[n] = ui.input_chips(label=n, value=v, new_value_mode="add", clearable=True).tooltip(d).props(f"readonly name={n}")
                        else:
                            outputs[n] = ui.input(label=n, value=v).tooltip(d).props(f"readonly name={n}")
                            
    async def _create_session_ids(self):
        await ui.run_javascript("""
            if (!localStorage.session_id) {
                localStorage.session_id = crypto.randomUUID();
            }
            if (!localStorage.model_id) {
                localStorage.model_id = crypto.randomUUID();
            }
        """)
        session_id, model_id = await self._load_session_ids()        
        with ui.footer():
            with ui.column().classes("w-full gap-1"):
                ui.input(label="Session ID", value=session_id).classes("text-white").props("readonly name=session_id").tooltip("Session ID - identifies your session and allows to store session specific data models")
                ui.input(label="Model ID", value=model_id).classes("text-white").props("readonly name=model_id").tooltip("Model ID - identifies your data model")
        
    async def _load_session_ids(self) -> Tuple[str, str]:
        session_id = await ui.run_javascript("localStorage.session_id")
        model_id = await ui.run_javascript("localStorage.model_id")
        return session_id, model_id