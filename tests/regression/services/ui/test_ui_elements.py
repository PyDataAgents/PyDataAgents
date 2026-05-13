from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ui.UIBufferPage import UIBufferPage
from pydag.services.ui.UIElements import BufferTable, PlotCard
from pydag.services.ui.UIService import UIService


def test_000():
    uis = UIService()
    p = UIBufferPage(uis)
    
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
    
