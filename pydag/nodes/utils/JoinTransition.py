from ..Transition import Transition


class JoinTransition(Transition):
    
    def __post_init__(self):
        super().__post_init__()
        self.visited_from_parents : dict[str, str] = dict()
        
    def _on_check(self) -> bool:
        for node in self._parents:
            if not node.id in self.visited_from_parents:
                return False
        self.visited_from_parents.clear()
        return True
