

from    t8dev.toolset.setup import *

class CSCP(Setup):

    def __init__(self):
        super().__init__()
        self.source_archive = 'binary.7z'
        self.source_url = 'http://takeda-toshiya.my.coocan.jp/common/'

    def toolset_name(self):
        return 'cscp'

    def check_installed(self):
        return False

TOOLSET_CLASS = CSCP
