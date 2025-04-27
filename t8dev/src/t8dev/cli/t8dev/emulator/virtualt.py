' VirtualT TRS-80 Model 100 (and friends) emulator suite. '

from    shutil  import  copy, copytree
import  os

from    t8dev.cli.t8dev.emulator.suite  import Suite
import  t8dev.path  as path
import  t8dev.run as run

class VirtualT(Suite):

    suitedesc = 'VirtualT TRS-80 Model 100 (and friends)'

    @classmethod
    def setargparser(cls, parser):  return

    def run(self):
        copytree(path.tool('src/virtualt/ROMs/'),
                 self.emudir('ROMs'),
                 dirs_exist_ok=True)

        #   `contextlib.chdir` is not available until Python 3.11.
        #   If we need to do more of this, we should build or own decorator.
        oldcwd = os.getcwd()
        try:
            os.chdir(self.emudir())
            run.tool('virtualt')
        finally:
            os.chdir(oldcwd)
