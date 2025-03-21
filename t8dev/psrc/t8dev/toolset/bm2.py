'''
    bm2 - Hitachi MB-6885 Basic Master Jr. Emulator

    - The bm2 homepage_ provides a high-level overview of what the emulator
      is and does, and many screenshots.
    - ``$T8_PROJDIR/.build/tool/src/bm2/readme.txt`` contains the original
      documentation, which is reasonably useful.
    - retroabandon/hitachi-mb688x_ has another copy of the source code and
      further notes from reverse-engineering it.

    .. _homepage: http://ver0.sakura.ne.jp/pc/#bm2
    .. _retroabandon/hitachi-mb688x: https://gitlab.com/retroabandon/hitachi-mb688x
'''

from    t8dev.toolset.setup  import *

class BM2(Setup):

    def __init__(self):
        super().__init__()
        self.source_url = 'http://ver0.sakura.ne.jp/pc/'
        #   See README in the bm2src repo for why we use it instead of above.
        self.source_url = 'https://github.com/mc68-net/bm2src/raw/refs/heads/main/archive/'
        self.source_archive = 'bm2src_20240817.tgz'
        self.source_sha = \
            '1eeec77742099a89c231d02c2bebf801ba6ba7b9476a194e20f8e76f9b7d50bc'
        self.source_tar_strip = 1   # drop top-level `bm2/` in tarfile

    def check_installed(self):
        ''' There seems to be no way to run the program and have it
            immediately exit rather than start up the emulation in the
            window, so we settle for just seeing that the binary is there,
            is a proper file, and is executable.
        '''
        bm2 = self.pdir('bin').joinpath('bm2')
        #   /usr/bin/test deferences all symlinks before testing
        return checkrun(['/usr/bin/test', '-f', bm2, '-a', '-x', bm2])

    DEPENDENCIES = (
        ('libsdl2-dev',             ('sdl2-config', '--version')),
    )

    def build(self):
        self.make_src()

    def install(self):
        #   Cannot `make install` because it's `cp $(EXE) /usr/local/bin`.
        dest = self.pdir('bin').joinpath('bm2')
        if not dest.exists():
            self.symlink_toolbin(self.srcdir(), 'bm2')

TOOLSET_CLASS = BM2
