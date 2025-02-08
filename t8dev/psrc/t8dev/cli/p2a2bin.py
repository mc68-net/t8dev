#!/usr/bin/env python3
#
#   p2a2bin - convert AS .p file to Apple II DOS 3.3 binary (`B`) file
#
#   Output to stdout; redirect it if you need.
#

from    os  import fdopen
from    struct  import pack
from    sys  import argv, stdout

from    t8dev  import path
from    t8dev.cli  import exits
from    binary.tool.asl  import parse_obj_fromfile


def load_image(fname):
    if '.' not in fname: fname += '.p'
    if '/' not in fname: fname = path.obj('src', fname)
    return parse_obj_fromfile(fname)

def print_a2bin(mi):
    length = mi.contiglen()
    start  = mi.startaddr       # XXX relies on contiglen() setting this

    if mi.entrypoint is not None and mi.entrypoint != mi.startaddr:
        raise ValueError('Start address {:04X} != {:04X} entrypoint' \
            .format(mi.startaddr, mi.entrypoint))
    if mi.contiglen() > 0x7FFF:
        #   DOS 3.3 does not support binary files >= 32 KB.
        raise ValueError('Length {:04X} > $7FFF'.format(mi.contiglen()))

    output = fdopen(stdout.fileno(), 'wb')  # reopen stdout as binary
    output.write(pack('<h', mi.startaddr))
    output.write(pack('<h', mi.contiglen()))
    output.write(mi.contigbytes())

def main():
    if len(argv) != 2:  exits.usage('p2a2bin <file>')
    print_a2bin(load_image(argv[1]))
