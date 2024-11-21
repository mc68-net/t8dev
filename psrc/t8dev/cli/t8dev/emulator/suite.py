' Superclass for an emulator suite. '

from    abc  import ABC, abstractmethod
import  t8dev.path  as path

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
        ''' Configure an emulator suite to run a particular emulator.

            This expects subclasses to follow certain conventions about the
            command-line arguments `args`.
            - If this suite allows specification of a specific emulator at
              the command line (some do not, and some suites are just a
              single emulator), it expects that the emulator is specified
              with an `emulator` argument, and will set `self.emulator` to
              that. Otherwise, `self.emulator` is set to `None`.
        '''
        self.args = args
        if hasattr(self.args, 'emulator'):
            self.emulator = self.args.emulator
        else:
            self.emulator = None

    @abstractmethod
    def run(self): ...

    def emudir(self, *components):
        ''' Return a `Path` under the directory for this emulation run.

            The base directory for the emulation run is ``.build/emulator/`
            followed by the suite name and, if present, the emulator name.
            That directory will be created if it doesn't already exist;
            nothing below that is created automatically.
        '''
        emudir_components = ['emulator', self.suitename()]
        if self.emulator is not None:
            emudir_components.append(self.emulator)
        emudir = path.build(*emudir_components)
        emudir.mkdir(exist_ok=True, parents=True)
        return emudir.joinpath(*components)
