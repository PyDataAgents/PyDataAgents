import json
from dataclasses import dataclass, field
import quickjs


from ...agents.Agent import Agent
from ..BufferNode import BufferNode
from ..NodeException import NodeException
from ..Transition import Transition


@dataclass
class IfTransition(BufferNode, Transition):
    """ This `Transition` routes the parent data as json to a javascript expression and evaluates a boolean operator.
    If it evaluates True, the check() transfers the data to the child nodes.
    <br>
    <br>
    Example:
    <br>>>data = {d:[1.0, 2.3, 4.1, -0.9], b:[True, False, True, False]}
    <br>>>expression = 'data.d > 1.0 && data.b'
    """

    expression : str = field(default="true", metadata={"description": "javascript expression that must return a boolean"})
    
    def __post_init__(self):
        super().__post_init__()
        self._ctx = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._ctx = quickjs.Context()
        # protection against expensive expressions
        self._ctx.set_time_limit(0.1)
        self._ctx.set_memory_limit(8 * 1024 * 1024)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._ctx = None

    def _on_check(self) -> bool:
        if self._ctx is None:
            raise NodeException(f"{self.__class__.__name__} is not installed")
        data = self.get_parent_data(by_rows = True)
        checked : bool = False
        for row in data:
            try:
                self._ctx.set("json_obj", json.dumps(row))
                result = self._ctx.eval(f"""
                    (() => {{
                        const data = JSON.parse(json_obj);
                        return Boolean({self.expression});
                    }})()
                """)
                if bool(result):
                    self.add_data(row)
                    checked = True
            except quickjs.JSException as e:
                raise NodeException(f"Javascript {self.expression} could not be executed") from e
        return checked