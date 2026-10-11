from pydag.services.ServiceException import ServiceException


class StatemachineException(ServiceException):
    """Exception class for statemachine services"""
    
    def __init__(self, message: str):
        super().__init__(message)