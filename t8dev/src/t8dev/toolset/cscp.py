''' Common Source Code Project emulators

    Unfortunately these are distributed as .7z archives, which are a bit
    of a pain to extract. We've tried three different libraries:
    • py7zr: This is a pure Python implementation, which is perfect, except
      that it (or rather XZ/liblzma) doesn't support the BCJ2 filter
      needed to decompress binary.7z.
    • libarchive-c: Works quite well, but requires the libarchive shared
      library be installed, and apparently there are issues with that on Mac
      that require downloading a different version and setting LIBARCHIVE
      to point to that file.
    • patoolib: Doesn't do the extraction itself, but merely looks around
      the system to find one of a list of programs that it knows how to use
      to do the extraction.

    patoolib seems to be the least worst option, since at least it fairly
    clearly explains to the user what programs to look for if it can't find
    one to do the extraction, and seems likely to work on Unix, Windows
    and MacOS.

    That said, the package name with the required archiving tool is not
    always obvious.
    • Debian: `p7zip` provides `7zr`.

'''

from    patoolib  import extract_archive
from    t8dev.toolset.setup import *
import shutil
import os

class CSCP(Setup):

    def __init__(self):
        super().__init__()
        self.source_archive = 'binary.7z'
        self.source_url = 'http://takeda-toshiya.my.coocan.jp/common/'

    def toolset_name(self):
        return 'cscp'

    def bindir(self):
        return self.pdir('bin', 'cscp')

    def check_installed(self):
        return self.bindir().joinpath('z80tvgame_z80pio.exe').exists()

    def install(self):
        self.printaction('Installing from {}'.format(self.dlfile.name))

        extract_dir = self.pdir('extract', 'cscp')
        extract_archive(str(self.dlfile), outdir=extract_dir,
            interactive=False, verbosity=0)
        extract_root = extract_dir.joinpath('binary')

        source_dir = extract_root.joinpath('binay_win10')
        files = os.listdir(source_dir)
        for file in files:
            source_file = source_dir.joinpath(file)
            destination_file = self.bindir().joinpath(file)
            shutil.copy2(source_file, destination_file)

TOOLSET_CLASS = CSCP
