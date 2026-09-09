from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.SplitStringAction import SplitStringAction


def test_parse_filename_action_splits_parent_filename_into_output_keys():
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"file": "C:\\fake\\path\\sales_2024_09.csv"})

    link = LinkBufferAction()
    link.set_buffer(buf)

    action = SplitStringAction(
        delimiter="_",
        input_keys=["file"],
        output_keys=["postfix", "year", "month"],
    )
    action.add_parent(link)
    action.install()

    action.execute()

    data = action.get_buffer().data()
    assert data["postfix"][0] == "sales"
    assert data["year"][0] == "2024"
    assert data["month"][0] == "09"
    
def test_filename_parse_action_with_parsing_functions():
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"file": "C:\\fake\\path\\sales_2024_09.csv"})

    link = LinkBufferAction()
    link.set_buffer(buf)

    func1 = """
    def force_numeric(s : str) -> float | int:
        try:
            return int(s)
        except:
            try:
                return float(s)
            except:
                return s                
        """
    
    pfuncs = [None, func1, func1]
    
    action = SplitStringAction(
        delimiter="_",
        input_keys=["file"],
        output_keys=["postfix", "year", "month"],
        parsing_functions=pfuncs
    )
    action.add_parent(link)
    action.install()

    action.execute()

    data = action.get_buffer().data()
    assert data["postfix"][0] == "sales"
    assert data["year"][0] == 2024
    assert data["month"][0] == 9
