''' cli.t8dev emulator commands

    e help              help function for emulation commands
    e list              lists all of the suites available e.g. cscp, vice etc
    e cscp list         lists all available emulators within suite
    e cscp tk85         specific emulator from cscp suite
    e cscp pc8001
    e vice x64
    e openmsx           suite should have multiple MSX machine in it?
    e linapple
    e runcpm            probably no suite here, because just the one
'''

from    pathlib  import Path
from    shutil  import  copy, copyfile, get_terminal_size
from    sys  import exit, stderr
from    urllib.request  import HTTPError, urlopen
import  os
import  textwrap

from    binary.romimage  import RomImage
from    t8dev.cli  import exits
from    t8dev.cli.t8dev.util  import err, cwd, runtool, vprint
import  t8dev.path  as path
import  t8dev.run  as run


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

    #   XXX This requires that wine be installed (on Linux) and the
    #   emulators be extracted to .build/tool/bin/cscp/, which is
    #   done by `t8dev buildtoolset cscp`. We should give a hint
    #   about doing that if the emulators are not present.

    #   VENDOR_ROM entries may be for an actual CSCP emulator name, or may
    #   be alternate configurations that load a different set of ROMs
    #   (e.g., `tk80` below). The alternate ROM configurations include an
    #   `_emulator` entry which is not a ROM image but indicates the actual
    #   name of the emulator to use (e.g., `tk80bs` for the `tk80` entry
    #   below).
    VENDOR_ROM = {
        'pc8001': {
            'N80.ROM': 'https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/N80_11.bin',
            'KANJI1.ROM': '@1000:https://gitlab.com/retroabandon/pc8001-re/-/raw/main/rom/80/FONT80.bin',
        },
        'tk80': {
            '_emulator': 'tk80bs',
            'TK80.ROM':             # $0000-$07FF fill $FF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK80.bin',
            'EXT.ROM': None,        # $0C00-$7BFF
            'BSMON.ROM': None,      # $F000-$FFFF
        },
        'tk80bs': {
            #   With TK80.ROM not present (file size 0) the emulator sets
            #   `jp $F000` at RST 0 and `jp $83DD` at RST 7, like the
            #   `tk80.dummy` ROM that MAME uses.
            'TK80.ROM': None,       # $0000-$07FF fill $FF
            'EXT.ROM':              # $0C00-$7BFF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/80BS-clone/etkroms3/Ext.rom',
            #   If this ROM _is_ present (file size >0) the emulator sets
            #   `jp $83DD` at RST 7 (patching TK80.ROM if present).
            'BSMON.ROM':            # $F000-$FFFF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/80BS-clone/etkroms3/bsmon.rom',
            #   Only one of LV[12]BASIC.ROM is read based on the boot mode.
            'LV1BASIC.ROM':         # $E000-$EFFF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/80BS-clone/etkroms/L1CB.ROM',
            'LV2BASIC.ROM':         # $D000-$EFFF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/80BS-clone/etkroms3/LV2BASIC.ROM',
            'FONT.ROM':             # chargen addr space
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/80BS-clone/etkroms3/font.rom',
        },
        'tk85': {
            'TK85.ROM':             # $0000-$07FF fill $FF
                'https://gitlab.com/retroabandon/tk80-re/-/raw/main/rom/TK85.bin',
            'EXT.ROM': None,        # $0C00-$7BFF
        },
    }

    def run(self):
        if not self.args:
            exits.arg("Missing emulator name. Use 'list' for list of emulators.")

        self.set_bindir()
        self.emulator = emulator = self.args.pop(0)
        if emulator == 'list':
            self.print_emulators()
            return
        elif emulator not in (self.emulator_exes() + list(self.VENDOR_ROM)):
            exits.arg(f"Bad emulator name '{emulator}'."
                " Use 'list' for list of emulators.")
        else:
            emuexe = self.setup_emudir(emulator)
            cmd = [str(self.emudir(emuexe))]
            if os.name != 'nt':  cmd = ['wine'] + cmd
            runtool(*cmd)

    def emulator_exes(self):
        return [ p.stem for p in sorted(self.bindir.glob('*.exe')) ]

    def print_emulators(self):
        rom_configs = [ name
            for name, roms in self.VENDOR_ROM.items()
            if not roms.get('_emulator') ]
        print('With ROM configurations:'); self.format_list(rom_configs)

        alt_configs = [ f"{name} ({roms.get('_emulator')})"
            for name, roms in self.VENDOR_ROM.items()
            if roms.get('_emulator') ]
        print('Alternate ROM configurations:'); self.format_list(alt_configs)

        exes = filter(lambda x: x not in rom_configs, self.emulator_exes())
        print('Without ROM configurations:'); self.format_list(exes)

    @staticmethod
    def format_list(l):
        cols = get_terminal_size().columns - 3
        print(textwrap.fill(' '.join(l), width=cols,
            initial_indent='  ', subsequent_indent='  '))

    def emudir(self, *components):
        ' Return a `Path` in the directory for this emulation run. '
        emudir = path.build('emulator', self.emulator)
        emudir.mkdir(exist_ok=True, parents=True)
        return emudir.joinpath(*components)

    def setup_emudir(self, emulator):
        ' Called with CWD set to the dir for this emulation run. '

        # This may be overridden by VENDOR_ROM '_emulator' entry.
        emuexe = emulator + '.exe'

        roms = self.VENDOR_ROM.get(emulator, {})
        if not roms:  exits.warn(
            f'WARNING: CSCP emulator {emulator} has no ROM configuration.')
        for filename, loadspec in roms.items():
            if filename == '_emulator':
                emuexe = loadspec + '.exe'
                continue
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

        self.emudir(emuexe).unlink(missing_ok=True)
        #   Wine emulates Windows *really* well and throws up on
        #   symlinks, so we must copy the binary.
        copyfile(path.tool('bin/cscp', emuexe), self.emudir(emuexe))

        return emuexe

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
    #   XXX This requires that RunCPM be in the path. We should check this
    #   and suggest `t8dev buildtoolset RunCPM` if it's not present.

    def run(self):
        self.emudir = path.build('emulator', self.suitename())
        self.setup_emudir()
        with cwd(self.emudir): run.tool('RunCPM')

    def setup_emudir(self):
        A0 = Path('./A/0'); B0 = Path('./B/0'); C0 = Path('./C/0')
        with cwd(self.emudir):
            for drive in (A0, B0, C0):
                drive.mkdir(exist_ok=True, parents=True)
        #   Copy specified files to drive A.
        for file in map(Path, self.args):
           self.copycpmfile(file, A0)
        #   Copy standard CP/M commands to drive C, if they are present.
        #   These can be installed with `t8dev buildtoolset osimg`.
        for file in path.tool('src/osimg/cpm/2.2/').glob('*'):
           self.copycpmfile(file, C0)

    def copycpmfile(self, src:Path, dir:Path):
        ''' Copy `src` to the `dir` directory under emudir.

            This converts filenames to all upper-case because, while RunCPM
            will show lower-case filenames (as upper case) in a directory
            listing, it will not find them if you try to run them as
            commands. This will blindly overwrite existing files, which can
            cause a different file to be overwritten if you run this with
            filenames differing only in case.

            We copy instead of creating a symlink so that files modified in
            the emulator can be compared with the originals.
        '''
        dest = Path(dir, src.name.upper())
        vprint(1, 'RunCPM', f'{str(dest):>16} ← {path.pretty(src)}')
        copyfile(src, self.emudir.joinpath(dest))


####################################################################

SUITES = dict([ (s.suitename(), s) for s in [
    CSCP, Linapple, OpenMSX, RunCPM, VICE]])
