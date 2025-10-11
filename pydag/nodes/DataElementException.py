class DataElementException(Exception):
    
    def __init__(self, message):
        super().add_note(message)