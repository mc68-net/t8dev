''' testmc.tmc: testmc command line simulator

    This is a command-line version of the CPU simulators that has
    a very basic I/O system, using a machine-specific BIOS defined
    in the `testmc.*.tmc` modules.
'''

from    importlib.resources  import files as resfiles
from    functools  import partial
from    os  import isatty
from    pathlib  import Path
from    sys  import stdin, stdout
from    traceback  import print_exception
from    types  import ModuleType as module
import  argparse
import  termios, tty

import  t8dev.cli.exits as exits, t8dev.path as path
import  testmc

def main():
    args = parseargs()
    simulator = matchcpu(args.cpu)
    if simulator is None:
        exits.arg(f"Cannot find CPU simulator matching '{args.cpu}'\n"
            '(Use -L to list simulators.)')
    cpuname, cpumodule = simulator
    #   XXX This thing where the CPU name is separate from the CPU module
    #   (i.e., mapped in SIMULATORS) is a bit awkward; we should look at
    #   finding a way to have the module or Machine know its own CPU name.
    exec(cpuname, cpumodule, binpath(cpuname, args.file))

def parseargs(args=None):
    parser = argparse.ArgumentParser(description='tmc XXX', epilog='XXX')
    a = parser.add_argument
    a('-D', '--print-dir', action='store_true',
        help='XXX print dir with tmc support files for given CPU')
    a('-L', '--list-simulators', nargs=0, action=ListSimulators,
        help='Print a list of available simulators.')
    a('cpu', help='select CPU simulator')
    a('file', help='file to load and run (.p added if necessary)')
    return parser.parse_args(args)

class ListSimulators(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        print('tmc simulators:', ', '.join(testmc.SIMULATORS.keys()))
        exit(0)

def matchcpu(cpustr) -> tuple[str,module]|None:
    ''' Find a simulator name and module whose name matches `cpustr`, which may
        be any substring of the module name as listed in `testmc.SIMULATORS`.
        Returns `None` if not found.
    '''
    for name, module in testmc.SIMULATORS.items():
        if cpustr in name: return (name, module)
    return None

def binpath(cpu:str, binpath:str) -> Path:
    if '.' not in binpath: binpath += '.p'
    if '/' not in binpath: binpath = path.obj('exe', 'tmc', cpu, binpath)
    return Path(binpath)

####################################################################

def exec(cpuname:str, cpumodule:module, exepath:Path):
    print(f'{cpumodule.__name__} executing {path.pretty(exepath)}')
    m = cpumodule.Machine()
    entrypoint = m.load(exepath)
    setupIO(m, cpuname)

    m.reset()
    #   If we have an entrypoint in the object file, we start there for
    #   convenience. Otherwise we start at the reset vector.
    if entrypoint: m.pc = entrypoint

    try:
        while True: m.step()
    except Exception as ex:
        tb = ex.__traceback__
        tb = None   # Traceback not usually useful. Add option to print it?
        print_exception(None, ex, tb)

def setupIO(m, cpuname):
    ''' Load the BIOS, set up `charoutport` for writes to stdout,
        `charinport` for blocking reads from stdin, and `exitport`
        for exiting the process.
    '''
    bioscode = path.obj('testmc', cpuname, 'tmc/bioscode.p')
    m.load(bioscode, mergestyle='prefcur', setPC=False)
    m.setio(m.symtab.charinport, consoleio)
    m.setio(m.symtab.exitport, partial(exitport, exitcmd=m.symtab.exitportcmd))

def consoleio(_addr, char):
    if char is None:
        return getchar()
    else:
        stdout.buffer.write(bytes([char]))
        stdout.buffer.flush()

def exitport(_addr, val, exitcmd=None):
    if val == exitcmd: exit(0)
    return exitcmd

def getchar():
    ''' Blocking read of a charater from stdin, in raw mode.

        This enables raw mode only during the read so that the user can
        still generate a SIGINT to kill the program when it's not waiting
        for input.

        XXX Echo probably should be disabled all the time to avoid echoing
        typeahead.
    '''
    fd = stdin.fileno()
    if not isatty(fd):
        return stdin.buffer.read(1)[0]
    else:
        prevattrs = termios.tcgetattr(fd)
        try:
            tty.setraw(fd, termios.TCSADRAIN)
            c = stdin.buffer.read(1)[0]
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, prevattrs)
        return c

