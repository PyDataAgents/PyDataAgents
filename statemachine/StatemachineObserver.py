from PyDataGrabber.mappings.Observer import Observer
from PyDataGrabber.statemachine.Statemachine import Statemachine


class StatemachineObserver(Observer):
    """
    Observer for the StatemachineService.
    This observer is be used to start the statemachine in a separate thread
    """
        
    def __init__(self, statemachine: Statemachine):
        super().__init__()
        self.statemachine = statemachine

    def observe(self):
        self.statemachine.start()
    
    def unobserve(self):
        """
        Unobserve the statemachine.
        This method is called when the statemachine is being stopped
        """
        if self.statemachine.is_running:
            self.statemachine.stop()