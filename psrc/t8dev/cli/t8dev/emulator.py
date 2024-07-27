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
        #   Currently our default is to load TK80.ROM and not load BSMON.ROM,
        #   which produces a "normal" unexpanded TK-80.
        #   - If BSMON.ROM is supplied, the emulator patches the start
        #     vector (RST 0) to jump to the BSMON start (`jp $F000`). This
        #     will give an expanded TK80BS running in BASIC mode.
        #   - If TK80.ROM is _not_ supplied, the emulator patches the start
        #     vector as above and RST 7 to `jp $83DD` (for the hardware
        #     interrupt?), giving a TK80BS in BASIC without original TK-80
        #     ROM functionality.
        #   We need to update r8format's binary.romimage to allow us to
        #   supply patch specs like `tk80=-` to clear the ROM image (thus
        #   removing any loaded defaults) so we can supply nice defaults
        #   here but easily allow users to undo them.
        'tk80bs': {
            #   If this ROM is _not_ present (file size 0) the emulator sets
            #   `jp $F000` at RST 0 and `jp $83DD` at RST 7.
            'TK80.ROM':         # $0000-$07FF fill $FF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK80.bin',
            'EXT.ROM': None,    # $0C00-$7BFF
            #   If this ROM _is_ present (file size >0) the emulator sets
            #   `jp $83DD` at RST 7.
            'BSMON.ROM':        # $F000-$FFFF
                None,
        },
        'tk85': {
            'TK85.ROM':         # $0000-$07FF fill $FF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK85.bin',
            'EXT.ROM': None,    # $0C00-$7BFF
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
            try:
                ri = RomImage(filename, path.download('rom-image'), loadspec)
                ri.patches(self.args)   # removes args it used and patched
            except FileNotFoundError as ex:
                exits.err(ex)
            except HTTPError as ex:
                exits.err(f'{ex}: {ex.url}')
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
