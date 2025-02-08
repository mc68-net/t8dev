'''
    ctools, used for creating/manipulating Commodore 64/128 CP/M images.

    This will fetch from `source_repo` and build the `source_ref`
    branch, if necessary.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    t8dev.toolset.setup import *

class Ctools(Setup):

    def __init__(self):
        super().__init__()
        #   This is Michael Steil's slightly modified version which
        #   works with modern C compilers. There are various other versions
        #   out there as well, but this seems easiest.
        self.source_repo = 'https://github.com/mist64/ctools.git'
        #self.source_ref  = 'xxxxxxx'

    def check_installed(self):
        return checkrun( ['ctools', '--help'], 0, b'ctools V0.4')

    def build(self):
        self.make_src(subdir='src/')

    def install(self):
        bins = ('biosdump', 'cformat', 'ctools', 'd64dump', )
        for path in bins:
            self.symlink_toolbin(self.srcdir(), 'src', path)

TOOLSET_CLASS = Ctools
