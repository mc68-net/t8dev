''' cli.t8dev emulator commands

    e help              help function for emulation commands
    e list              lists all of the suites available e.g. cscp, vice etc
    e cscp list         lists all available emulators within suite
    e cscp tk85
    e cscp pc8001
    e vice x64
    e openmsx
    e linapple
    e runcpm
'''

from    pathlib  import Path
from    shutil  import  copyfile, copyfileobj, get_terminal_size
from    sys  import exit, stderr
from    urllib.request  import HTTPError, urlopen
import  textwrap

from    binary.romimage  import RomImage
from    t8dev.cli  import exits
from    t8dev.cli.t8dev.util  import err, cwd, runtool
import  t8dev.path  as path


####################################################################

def emulator(args):
    '''
    '''
    if not args:
        exits.arg("arguments required; 'help' for help")
    if args[0] == 'help':
        print('Usage: t8dev emulate SUITE [emulator] [args...]')
        print('       t8dev emulate list    # list emulator suites')
        exit(0)
    if args[0] == 'list':
        print('Emulator suites:')
        for c in sorted(SUITES): print(f'  {c}')
        exit(0)
    cls = SUITES.get(args[0], None)
    if cls is None:
        exits.arg(f"Bad suite name '{args[0]}'. Use 'list' for list of suites.")
    suite = cls(args[1:])
    suite.run()

####################################################################

class Suite:

    def __init__(self, args):
        self.args = args

    def run(self):
        exits.arg(f'{self}: unimplemented (args={self.args})')

    @classmethod
    def suitename(cls):
        return cls.__name__.lower()

class CSCP(Suite):

    VENDOR_ROM = {
        'tk85': {
            'TK85.ROM': 'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK85.bin'
        },
        'pc8001': {
            'N80.ROM': 'https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/N80_11.bin',
            'KANJI1.ROM': '@1000:https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/FONT80.bin',
        },
    }

    def run(self):
        if not self.args:
            exits.arg("Missing emulator name. Use 'list' for list of emulators.")

        self.set_bindir()
        emulist = [ p.stem for p in sorted(self.bindir.glob('*.exe')) ]
        self.emulator = emulator = self.args.pop(0)
        if emulator == 'list':
            cols = get_terminal_size().columns - 1
            print(textwrap.fill(' '.join(emulist), width=cols))
            return
        elif emulator not in emulist:
            exits.arg(f"Bad emulator name '{emulator}'."
                " Use 'list' for list of emulators.")
        else:
            self.setup_emudir(emulator)
            runtool('wine', str(self.emudir(emulator + '.exe')))

    def emudir(self, *components):
        ' Return a `Path` in the directory for this emulation run. '
        emudir = path.build('emulator', self.emulator)
        emudir.mkdir(exist_ok=True, parents=True)
        return emudir.joinpath(*components)

    def setup_emudir(self, emulator):
        ' Called with CWD set to the dir for this emulation run. '
        emuexe = emulator + '.exe'
        self.emudir(emuexe).unlink(missing_ok=True)
        #   Wine emulates Windows *really* well and throws up on
        #   symlinks, so we must copy the binary.
        copyfile(path.tool('bin/cscp', emuexe), self.emudir(emuexe))

        roms = self.VENDOR_ROM.get(emulator, {})
        if not roms:  exits.warn(
            f'WARNING: CSCP emulator {emulator} has no ROM configuration.')
        for filename, loadspec in roms.items():
            ri = RomImage(filename, path.download('rom-image'), loadspec)
            ri.patches(self.args)   # removes args it used and patched
            ri.writefile(self.emudir(filename))
        if self.args:
            exits.arg('Unknown arguments:', *[ f'  {arg}' for arg in self.args ])

    def set_bindir(self):
        import t8dev.toolset.cscp
        toolset = t8dev.toolset.cscp.CSCP()
        toolset.setbuilddir()           # XXX toolset.__init__()
        toolset.setpath()               # should be doing this?
        self.bindir = toolset.bindir()


class VICE(Suite):
    pass

class OpenMSX(Suite):
    pass

class Linapple(Suite):
    pass

class RunCPM(Suite):

    def run(self):
        emudir = path.build('emulator', self.suitename())
        emu = emudir.joinpath('RunCPM')
        with cwd(emudir):  self.setup_emudir(emu)
        runtool(emu)

    def setup_emudir(self, emu):
        emu.unlink(missing_ok=True)
        #   XXX link instead of copy? This doesn't run on Windows, so....
        emu.symlink_to(f'../../tool/bin/{emu.name}')

        Path('./A/0').mkdir(exist_ok=True, parents=True)
        Path('./B/0').mkdir(exist_ok=True, parents=True)

####################################################################

SUITES = dict([ (s.suitename(), s) for s in [
    CSCP, Linapple, OpenMSX, RunCPM, VICE]])
