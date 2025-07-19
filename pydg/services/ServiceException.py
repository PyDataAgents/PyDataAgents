class ServiceException(Exception):
    """
    Custom exception class for the Service module.
    
    This exception is raised when there is an error in the Service module.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message