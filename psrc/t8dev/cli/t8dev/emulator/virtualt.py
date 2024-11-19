' VirtualT TRS-80 Model 100 (and friends) emulator suite. '

from    shutil  import  copyfile, get_terminal_size
from    urllib.request  import HTTPError
import  textwrap

from    binary.romimage  import RomImage
from    t8dev.cli.t8dev.emulator.suite  import Suite
from    t8dev.cli.t8dev.util  import runtool
import  os
import  t8dev.path  as path

class VirtualT(Suite):

    suitedesc = 'VirtualT TRS-80 Model 100 (and friends)'

    @classmethod
    def setargparser(cls, parser):
        return
