class AgentElementException(Exception):
    """
    Custom exception class for the agent module.
    
    This exception is raised when there is an error in the agent element module.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message