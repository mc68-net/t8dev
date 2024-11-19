' Superclass for an emulator suite. '

from    abc  import ABC, abstractmethod

class Suite(ABC):

    @classmethod
    def suitename(cls):
        return cls.__name__.lower()

    @classmethod
    def setargparser(cls, parser):
        ''' This is given a parser for the subcommand for this
            emulator suite; override this to add add arguments to it.
        '''

    def __init__(self, args):
        self.args = args

    @abstractmethod
    def run(self): ...
