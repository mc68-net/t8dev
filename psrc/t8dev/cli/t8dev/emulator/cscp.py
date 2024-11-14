' Common Source Code Projects (Japanese home computers) emulator suite '

from    shutil  import  copyfile, get_terminal_size
from    urllib.request  import HTTPError
import  textwrap

from    binary.romimage  import RomImage
from    t8dev.cli.t8dev.emulator.suite  import Suite
from    t8dev.cli.t8dev.util  import runtool
import  os
import  t8dev.path  as path

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

