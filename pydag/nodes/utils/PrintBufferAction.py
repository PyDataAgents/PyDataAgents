from dataclasses import dataclass
from loguru import logger


from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.utils.DataUtils import DataUtils


@dataclass
class PrintBufferAction(BufferNode, Action):
    """ utility `Action` to print the parents' results

    Args:
        BufferNode (_type_): _description_
        Action (_type_): _description_
    """
    
    def _on_execute(self):
        data = self.get_parent_data()
        rows = DataUtils.dict_to_list(data)
        for row in rows:
            logger.info(row)