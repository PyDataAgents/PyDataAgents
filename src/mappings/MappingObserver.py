from abc import abstractmethod

from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement


class MappingObserver(GrabberElement):

    @abstractmethod
    def observe():
        pass
