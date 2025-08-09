class AgentException(Exception):
    """
    Custom exception class for the Grabber module.
    
    This exception is raised when there is an error in the Grabber module.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message