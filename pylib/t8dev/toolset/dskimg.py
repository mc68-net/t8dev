#!/usr/bin/env python3
'''
    Fetch disk images used for testing.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    t8dev.toolset.setup  import *


class DiskImg(Setup):

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://gitlab.com/retroabandon/diskimg.git'

    def check_installed(self):
        #   Since the repo is only data files, we simply check to see
        #   if it's been cloned.
        return self.pdir('src').joinpath('diskimg', 'README.md').exists()

TOOLSET_CLASS = DiskImg
