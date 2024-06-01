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

from    t8dev.cli.t8dev.util  import cwd, runtool
import  t8dev.path  as path

####################################################################

def err(*msgs):
    print(*msgs, file=stderr)
    exit(1)

def argerr(*msgs):
    print(*msgs, file=stderr)
    exit(2)

def emulator(args):
    '''
    '''
    if not args:
        argerr("arguments required; 'help' for help")
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
        argerr(f"Bad suite name '{args[0]}'. Use 'list' for list of suites.")
    suite = cls(args[1:])
    suite.run()

####################################################################

class Suite:

    def __init__(self, args):
        self.args = args

    def run(self):
        argerr(f'{self}: unimplemented (args={self.args})')

    @classmethod
    def suitename(cls):
        return cls.__name__.lower()

    def romsrcdir(self, *components, mkdir=True):
        return path.download(
            'emulator/rom', self.suitename(), *components, mkdir=mkdir)

class CSCP(Suite):

    VENDOR_ROM = {
        'tk85': {
            'TK85.ROM': 'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK85.bin'
        },
        'pc8001': {
            'N80.ROM': 'https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/N80_11.bin',
            'KANJI1.ROM': 'https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/FONT80.bin',
        },
    }

    def run(self):
        if not self.args:
            argerr("Missing emulator name. Use 'list' for list of emulators.")

        self.set_bindir()
        emulist = [ p.stem for p in sorted(self.bindir.glob('*.exe')) ]
        emulator = self.args.pop(0)
        if emulator == 'list':
            cols = get_terminal_size().columns - 1
            print(textwrap.fill(' '.join(emulist), width=cols))
            return
        elif emulator not in emulist:
            argerr(f"Bad emulator name '{emulator}'."
                " Use 'list' for list of emulators.")
        else:
            emudir = path.build('emulator', emulator)
            with cwd(emudir):  self.setup_emudir(emulator)
            runtool('wine', str(emudir.joinpath(emulator + '.exe')))

    def setup_emudir(self, emulator):
        ' Called with CWD set to the dir for this emulation run. '
        emuexe = emulator + '.exe'
        Path(emuexe).unlink(missing_ok=True)
        #   Wine emulates Windows *really* well and throws up on
        #   symlinks, so we must copy the binary.
        copyfile(f'../../tool/bin/cscp/{emuexe}', emuexe)

        romsrcdir = self.romsrcdir(emulator)
        for filename, url in self.VENDOR_ROM[emulator].items():
            dlrom = romsrcdir.joinpath(filename)
            if not dlrom.exists():
                try:
                    with urlopen(url) as response:
                        with open(dlrom, 'wb') as f:
                            self.padrom(emulator, filename, f)
                            copyfileobj(response, f)
                except HTTPError as ex:
                    err(f'{ex} for {filename!r} from {url!r}')
            copyfile(dlrom, filename)

    def padrom(self, emulator, filename, f):
        ''' Certain files for certain emulators in the CSCP suite need to
            have padding in front of the ROM data because they're sort of
            pretending that it's a different kind of ROM (one that doesn't
            even exist for the original machine, in the case of the PC-8001
            "kanji ROM"). For the moment we just special case each instance
            here, but if we detect a pattern we may be able to generalise
            this.
        '''
        if emulator == 'pc8001':
            if filename == 'KANJI1.ROM':
                f.write(b'\x00' * 0x1000)

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
