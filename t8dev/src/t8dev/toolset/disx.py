#!/usr/bin/env python3
'''
    Configure for use of the disx disassembler.

    This will fetch from `source_repo` and build the `source_ref`
    branch, if necessary.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    t8dev.toolset.setup import *

class disx(Setup):

    def toolset_name(self):
        #   This name is mixed case, not lower case.
        #   (Not sure why we default to lower() of the class name.)
        return type(self).__name__

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://github.com/mc68-net/disx'

    def check_installed(self):
        #   We can't try to run this because it requires a proper filesystem
        #   setup for its disk image, so even if you `echo exit | RunCPM`
        #   it will still print out a ton of errors, if it even exits at all.
        return self.pdir('bin').joinpath('disx').exists()

    DEPENDENCIES = (
        ('pkg-config',          ('pkg-config', '--version')),
        ('libncurses-dev',      ('pkg-config', 'ncurses')),
    )

    def build(self):
        self.make_src()

    def install(self):
        self.symlink_toolbin(self.srcdir(), 'disx')

TOOLSET_CLASS = disx
