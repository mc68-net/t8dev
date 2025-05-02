''' VirtualT, a TRS-80 Model 100 and Kyocera KC 85 family emulator

    This cannot be run directly as it expects to find the ROMs/ and doc/
    directories under the current working directory. Use `t8dev emulator`
    to run it and it will set things up appropriately.
'''

from    os.path  import abspath, dirname
import  sys

from    t8dev.toolset.setup import *

class VirtualT(Setup):

    def __init__(self):
        super().__init__()
        #self.source_repo = 'https://git.code.sf.net/p/virtualt/code.git'
        #   The original sources didn't compile on Debian at the time
        #   this was created, so pull a version that's had a fix applied.
        self.source_repo = 'https://github.com/mc68-net/virtualt.git'
        self.source_ref  = 'fixes'

    def check_installed(self):
        #   `virtualt` itself always starts up and opens a window,
        #   regardless of command line args, so check a companion program.
        return checkrun( ['vt_client'], 1, b'vt_client')

    DEPENDENCIES = (
        ('pkg-config',            ('pkg-config', '--version')),
        ('libxft-dev',            ('pkg-config', 'xft')),
        ('libxinerama-dev',       ('pkg-config', 'xinerama')),
        ('libfontconfig-dev',     ('pkg-config', 'fontconfig')),
        ('libjpeg-dev',           ('pkg-config', 'libjpeg')),
        ('libfltk1.3-dev',        ('fltk-config', '--version')),
    )

    def build(self):
        self.make_src()

    def install(self):
        for path in ('virtualt', 'vt_client'):
            self.symlink_toolbin(self.srcdir(), path)

TOOLSET_CLASS = VirtualT
