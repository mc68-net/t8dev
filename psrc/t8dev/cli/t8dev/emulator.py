''' cli.t8dev emulator commands

    e help              help function for emulation commands
    e list              lists all of the suites available e.g. cscp, vice etc
    e cscp list         lists all available emulators within suite
    e cscp tk85
    e cscp pc8001
    e vice x64
    e openmsx
    e linapple
    e runcpm
'''

from    sys  import exit, stderr

def argerr(*msgs):
    print(*msgs, file=stderr)
    exit(2)

def emulator(args):
    '''
    '''
    if not args:
        argerr("arguments required; 'help' for help")
    if args[0] == 'help':
        print('Usage: t8dev emulate SUITE [emulator] [args...]')
        print('       t8dev emulate list    # list emulator suites')
        exit(0)
    if args[0] == 'list':
        print('Emulator suites:')
        for c in sorted(SUITES): print(f'  {c}')
        exit(0)
    cls = SUITES.get(args[0], None)
    if cls is None:
        argerr(f"Bad suite name '{args[0]}'. Use 'list' for list of suites.")
    suite = cls(args[1:])
    suite.run()

####################################################################

class Suite:

    def __init__(self, args):
        self.args = args

    def run(self):
        argerr(f'{self}: unimplemented (args={self.args})')

class CSCP(Suite):

    def run(self):
        if not self.args:
            argerr("Emulator name required. Use 'list' for list of emulators.")
        emulator = self.args.pop(0)
        if emulator == 'list':
            self.list_emulators()
            return
        print(f'XXX more cscp emu {emulator}')

    def list_emulators(self):
        print('XXX print list here')

class VICE(Suite):
    pass

class OpenMSX(Suite):
    pass

class Linapple(Suite):
    pass

class RunCPM(Suite):
    pass

SUITES = {
    'cscp':         CSCP,
    'linapple':     Linapple,
    'openmsx':      OpenMSX,
    'runcpm':       RunCPM,
    'vice':         VICE,
}
