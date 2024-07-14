#!/usr/bin/env python3
#
#  tmc6800 - load an AS .p file into the testmc.mc6800 simulator and run it
#

from    sys  import argv, stdin, stdout
from    os  import isatty
from    traceback  import print_exception
import  termios, tty

from    t8dev  import path
from    t8dev.cli  import exits
from    testmc.mc6800  import Machine
from    binary.tool.asl  import parse_obj_fromfile

def binname(fname):
    if '.' not in fname: fname += '.p'
    if '/' not in fname: fname = path.obj('exe', 'tmc68', fname)
    return fname

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

def consoleio(_addr, char):
    if char is None:
        return getchar()
    else:
        stdout.buffer.write(bytes([char]))
        stdout.buffer.flush()

def setupIO(m):
    ''' Load the BIOS and set up `charoutport` for writes to stdout and
        `charinport` for blocking reads from stdin.
    '''
    bioscode = path.obj('src/tmc68/bioscode.p')
    m.load(bioscode, mergestyle='prefcur', setPC=False)
    m.setio(0xC000, consoleio)

def exec(fname):
    m = Machine()
    entrypoint = m.load(fname)
    setupIO(m)
    if entrypoint is None:
        #   No entrypoint in object file; start at reset vector.
        m.setregs(m.Registers(pc=m.word(0xFFFE)))
    try:
        while True: m.step()
    except Exception as ex:
        tb = ex.__traceback__
        tb = None   # Traceback not usually useful. Add option to print it?
        print_exception(None, ex, tb)

def main():
    if len(argv) != 2: exits.usage('Usage: tmc6800 <file>')
    exec(binname(argv[1]))
