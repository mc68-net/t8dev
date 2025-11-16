

from t8dev.toolset.setup import *

class Zesarux(Setup):

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://github.com/chernandezba/zesarux'

    def check_installed(self):
        return checkrun( ['zesarux', '--version'], 0, b'ZEsarUX')

    def configure(self):
        subdir = 'src/'
        args = ('--enable-ssl',
            '--disable-caca', '--disable-aa', '--disable-cursesw',)
        cmd = ('./configure', '--prefix', self.pdir()) + args
        self.printaction(*cmd)
        runcmd(cmd, cwd=self.srcdir().joinpath(subdir))

    def build(self):
        self.make_src(subdir='src/')

    def install(self):
        #   $PREFIX/share/zesarux/ contains ROMs etc. required to run.
        self.make_src('install', subdir='src/')

TOOLSET_CLASS = Zesarux



