''' cli.t8dev emulator commands

    emu help            help function for emulation commands
    emu list            lists all of the suites available e.g. cscp, vice etc
    emu cscp list       lists all available emulators within suite
    emu cscp tk85       specific emulator from cscp suite
    emu cscp pc8001
    emu vice x64
    emu openmsx         suite should have multiple MSX machine in it?
    emu linapple
    emu runcpm          probably no suite here, because just the one
'''

from    pathlib  import Path
from    shutil  import  copy, copyfile, get_terminal_size
from    sys  import exit, stderr
from    urllib.request  import HTTPError, urlopen
from    zipfile  import ZipFile
import  os
import  textwrap

from    binary.romimage  import RomImage
from    t8dev.cli  import exits
from    t8dev.cli.t8dev.util  import err, cwd, runtool, vprint
from    t8dev.cpm  import compile_submit
import  t8dev.path  as path
import  t8dev.run  as run


####################################################################

def setargs_emulator(spgroup):
    pemu = spgroup.add_parser('emulator', aliases=['emulate', 'emu', 'em'],
        help='run an emulator')
    suitegroup = pemu.add_subparsers(dest='suite', required=True,
        title='Emulator suites', metavar='', help='')
    for sc in SUITE_CLASSES:
        p = suitegroup.add_parser(sc.suitename(), help=sc.suitedesc)
        p.set_defaults(func=run_emulator(sc))
        sc.setargparser(p)

def run_emulator(suiteclass):
    '   XXX This seems a bit of a hack.... '
    def run(args): e = suiteclass(args); return e.run()
    return run

class Suite:

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

    def run(self):
        exits.arg(f'{self}: unimplemented (args={self.args})')

class CSCP(Suite):
    #   XXX This requires that wine be installed (on Linux) and the
    #   emulators be extracted to .build/tool/bin/cscp/, which is
    #   done by `t8dev buildtoolset cscp`. We should give a hint
    #   about doing that if the emulators are not present.

    suitedesc = 'Comon Source Code Project emulators'

    @classmethod
    def setargparser(cls, parser):
        parser.add_argument('emulator',
            help="the emulator to run (use 'list' to list all emulators)")
        parser.add_argument('patchspecs', nargs='*', help='ROM patchspecs')

    def run(self):
        self.set_bindir()
        self.emulator = emulator = self.args.emulator
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
                #   Use applicable patchspecs and remove from list.
                ri.patches(self.args.patchspecs) 
            except FileNotFoundError as ex:
                exits.err(ex)
            except HTTPError as ex:
                exits.err(f'{ex}: {ex.url}')
            ri.writefile(self.emudir(filename))
        if self.args.patchspecs:
            unknowns = ' '.join(self.args.patchspecs)
            exits.arg(f'Unknown patchspecs for {self.emulator}: {unknowns}')

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

class VICE(Suite):
    suitedesc = 'CBM/Commdore 8-bit systems emulators'

class OpenMSX(Suite):
    suitedesc = 'MSX and related systems emulators'

class Linapple(Suite):
    suitedesc = 'Apple II emulator'

class RunCPM(Suite):
    #   XXX This requires that RunCPM be in the path. We should check this
    #   and suggest `t8dev buildtoolset RunCPM` if it's not present.

    suitedesc = 'RunCPM CP/M 2.x emulator'

    @classmethod
    def setargparser(cls, parser):
        parser.add_argument('-a', '--autorun', action='store_true',
            help='automatically run the .COM file given as first argument')
        parser.add_argument('file', nargs='*',
            help='file to copy to A: drive')

    def run(self):
        #   XXX We use `=X` to specify option X, because `-X' will be
        #   consumed by the t8dev options parser. We need to get that
        #   options parser to use subcommands that can have their own
        #   separate options.
        self.emudir = path.build('emulator', self.suitename())
        self.setup_emudir(self.args.autorun)
        with cwd(self.emudir):
            #   RunCPM clears the screen on start, as well as doing other
            #   less annoying bits termios terminal manipulation. Set the
            #   terminal type to `dumb` so that it doesn't do this.
            run.tool('RunCPM', envupdate={ 'TERM': 'dumb' })

    def setup_emudir(self, autorun=False):
        #   Set up drives.
        A0, B0, C0, D0 = drives = tuple( Path(f'./{d}/0') for d in 'ABCD' )
        with cwd(self.emudir):
            for drive in drives:  drive.mkdir(exist_ok=True, parents=True)

        #   Copy specified files to drive A.
        for file in map(Path, self.args.file):
           self.copycpmfile(file, A0)

        #   Copy standard CP/M commands to drive C, if they are present.
        #   These can be installed with `t8dev buildtoolset osimg`.
        for file in path.tool('src/osimg/cpm/2.2/').glob('*'):
           self.copycpmfile(file, C0)

        #   Copy RunCPM-supplied commands to drive D, if present.
        #   Note that this would be _required_ in order to get EXIT.COM
        #   if we were buildiing with a different CCP, which we might
        #   well want to do at some point.
        file = path.tool('src/RunCPM/DISK/A0.ZIP')
        if file.exists(): self.copycpmzip(file, D0, subdir='A/0/')

        #   Build `$$$.SUB` file if we're auto-running the first argument.
        if autorun:
            #   Using XXX.COM to run a program in RunCPM often works, but
            #   not always; e.g. `TMON100.COM` can't seem to find that
            #   file, while `TMON100` works. So make sure we drop `.COM`.
            commands = [Path(self.args.file[0]).stem.upper(), 'EXIT']
            vprint(1, 'RunCPM', f'autorun: {commands}')
            subdata = compile_submit(commands)
            with open(self.emudir.joinpath(A0, '$$$.SUB'), 'wb') as f:
                f.write(subdata)

    def copycpmfile(self, src:Path, dir:Path):
        ''' Copy `src` to the `dir` directory under `self.emudir`.

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

    def copycpmzip(self, src:Path, dir:Path, subdir:str=''):
        ''' Copy all files from the ZIP file `src` to the `dir` directory
            under `self.emudir`. This upper-cases the filenames in
            the same way that `copycpmfile` does.

            If `subdir` is given, only files underneath that directory in
            the ZIP file will be extracted, and that directory prefix will
            be removed from the extracted file. (Note that this is a `str`,
            not a `Path`, and you must include a trailing slash.)
        '''
        if subdir.startswith('/'): subdir = subdir[1:]
        assert subdir.endswith('/')
        vprint(1, 'RunCPM', f'{str(dir):>15}/ ← {path.pretty(src)}')
        with ZipFile(src) as zf:
            for entry in zf.infolist():
                if len(entry.filename) <= len(subdir): continue
                if not entry.filename.startswith(subdir): continue
                exfname = entry.filename[len(subdir):]
                vprint(2, 'RunCPM', f'extracting [{subdir}]{exfname}')
                with open(self.emudir.joinpath(dir, exfname), 'wb') as f:
                    f.write(zf.read(entry))


####################################################################

SUITE_CLASSES = [ CSCP, Linapple, OpenMSX, RunCPM, VICE ]

SUITES = dict([ (s.suitename(), s) for s in [
    CSCP, Linapple, OpenMSX, RunCPM, VICE]])
