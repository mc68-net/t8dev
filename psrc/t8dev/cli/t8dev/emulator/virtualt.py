' VirtualT TRS-80 Model 100 (and friends) emulator suite. '

from    contextlib  import chdir
from    shutil  import  copy, copytree

from    t8dev.cli.t8dev.emulator.suite  import Suite
from    t8dev.cli.t8dev.util  import runtool
import  t8dev.path  as path

class VirtualT(Suite):

    suitedesc = 'VirtualT TRS-80 Model 100 (and friends)'

    @classmethod
    def setargparser(cls, parser):  return

    def run(self):
        copytree(path.tool('src/virtualt/ROMs/'),
                 self.emudir('ROMs'),
                 dirs_exist_ok=True)
        with chdir(self.emudir()):
            runtool('virtualt')
