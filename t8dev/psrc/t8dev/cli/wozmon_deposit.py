#!/usr/bin/env python3

from    sys  import argv
from    t8dev  import path
from    t8dev.cli  import exits
from    binary.tool.asl  import parse_obj_fromfile

def load_image(fname):
    if '.' not in fname: fname += '.p'
    if '/' not in fname: fname = path.obj('src', fname)
    return parse_obj_fromfile(fname)

def print_wozinput(eol, mi):
    ''' Given a `binary.memimage.MemImage`, print it out in the form
        you would enter it into the Apple 1 Woz monitor.
    '''
    BYTES = 16                  # number of bytes per input line
    for rec in mi:
        data = rec.data
        addr = rec.addr
        index = 0
        while index < len(data):
            line = '{:04X}:'.format(addr)
            for i in range(index, index+BYTES):
                if i < len(data):
                    line += ' {:02X}'.format(data[i])
            print(line, end=eol)
            addr += BYTES
            index += BYTES

USAGE = 'wozmon-deposit -c|-n <file>'

def main():
    if len(argv) < 3: exits.usage(USAGE)
    if   argv[1] == '-c': eol = '\r'
    elif argv[1] == '-n': eol = '\n'
    else                : exits.usage(USAGE)
    print_wozinput(eol, load_image(argv[2]))
