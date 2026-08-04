class AppException(Exception):
    """
    Custom exception class for the app module.
    
    This exception is raised when there is an error in the app module.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message