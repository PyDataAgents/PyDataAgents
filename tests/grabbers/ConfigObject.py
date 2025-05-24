class ConfigObject:
    
    def __init__(self):
        self._prop1 = None
        self._prop2 = None
        
    @property
    def prop1(self):
        return self._prop1