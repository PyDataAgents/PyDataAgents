import os

from nicegui import ui

from pydag.agents.Agent import Agent
from pydag.agents.ui.UIDataModelPage import UIDataModelPage
from pydag.buffers.DictBuffer import DictBuffer
from pydag.agents.ui.UIBufferPage import UIBufferPage
from pydag.agents.ui.UIElements import BufferTable, EditableTable, PlotCard
from pydag.services.datamodel.DataModelService import DataModelService
from tests.regression.agents.ui.TableDataModel import TableDataModel


def test_000():
    ag = Agent()
    
    p = UIBufferPage(ag)    
    ag.add_ui_page(p)
    
    buf1 = DictBuffer()
    buf2 = DictBuffer()
    
    p.add_ui_component(PlotCard(p, buf1))
    p.add_ui_component(PlotCard(p, buf2))
    
    p.remove_ui_component(0)
    
    assert len(p.get_ui_components()) == 1, "could not delete ui element"


def test_buffer_table_data():
    table = BufferTable(None, DictBuffer())
    
    rows, columns = table._table_data({"a": [1, 2], "b": ["x", "y"]})
    
    assert rows == [
        {"__row_id__": 0, "a": 1, "b": "x"},
        {"__row_id__": 1, "a": 2, "b": "y"},
    ]
    assert [column["name"] for column in columns] == ["__row_id__", "a", "b"]
    
def _build_editable_table_ui():
    columns = {"A": "Column A", "B": "Column B"}
    data = [{"A": 1, "B": "a"},
            {"A": 2, "B": "b"}]
    t = EditableTable(columns=columns, data=data)
    
    def print_handler(d):
        print(d)
        
    t.on_change(print_handler)
    
    
def test_editable_table():
    os.environ.setdefault("NICEGUI_SCREEN_TEST_PORT", "10001")
    ui.run(reload=True, port=10001, root=_build_editable_table_ui)
    

def test_editable_table_in_datamodel():
    ag = Agent(with_ui=True, port=10001, dark_mode=False)
    
    dms = DataModelService()
    dms.set_model(TableDataModel)
    
    ag.add_service(dms)
    
    ag.add_ui_page(UIDataModelPage(ag, dms))
    
    ag.release()