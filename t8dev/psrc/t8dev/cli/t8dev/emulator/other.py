''' Emulator suites not large enough to deserve their own file yet.

    Many of these are incomplete.
'''

from    t8dev.cli.t8dev.emulator.suite  import Suite

class VICE(Suite):
    suitedesc = 'CBM/Commdore 8-bit systems emulators'

class OpenMSX(Suite):
    suitedesc = 'MSX and related systems emulators'

class Linapple(Suite):
    suitedesc = 'Apple II emulator'
