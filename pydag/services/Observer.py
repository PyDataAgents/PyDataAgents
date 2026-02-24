from abc import abstractmethod

class Observer():
                    
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def unobserve(self):
        pass
        

    