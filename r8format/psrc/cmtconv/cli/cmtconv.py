#!/usr/bin/env python3

from    site  import addsitedir
from    argparse import ArgumentParser
from    functools import partial
import  sys, os

import  cmtconv.formats as fm, cmtconv.logging as lg


parseint = partial(int, base=0)     # Parse an int recognizing 0xNN etc.

def parse_args():
    p = ArgumentParser(description='''
            Convert computer audio tape saves between various formats.''',
        epilog='''
            Giving no `output` argument will just read the input. This is
            useful for validation and, along with `-v`, for debugging.
        ''')
    a = p.add_argument

    a('-p', '--platform', metavar='P', default='JR-200',
        help="default 'JR-200'")
    a('-i', '--input-format', metavar='FMT')
    a('-o', '--output-format', metavar='FMT')
    a('-f', '--filename', metavar='FN', help='filename to store in tape data')
    a('-l', '--loadaddr', metavar='ADDR', type=parseint,
        help='load address to store in tape data')
    a('-t', '--filetype', metavar='TYPE', default=None,
        help='file type: BASIC or BINARY')
    a('-v', '--verbose', action='count', default=0)

    a('input', help="input file ('-' for stdin)")
    a('output', nargs='?', help="output file ('-' for stdout)")

    args = p.parse_args()
    lg.set_verbosity(args.verbose)

    #   Collect up optional parameters passed on to input and routines from
    #   formats module.
    args.reader_optargs = {}
    for argname in ('filename', 'loadaddr', 'filetype'):
        val = getattr(args, argname)
        if val is not None: args.reader_optargs[argname] = val

    args.input_format  = fm.guess_format(args.input_format, args.input)
    args.output_format = fm.guess_format(args.output_format, args.output)

    #   You'd think we could use FileType, but in Python 3.5 even if
    #   you give it mode 'b', it still uses stdin/stdout as text.
    if args.input == '-':               args.input = sys.stdin.buffer
    else:                               args.input = open(args.input, 'br')
    if args.output == '-':              args.output = sys.stdout.buffer
    elif args.output is not None:       args.output = open(args.output, 'bw')

    return args

def main():
    args = parse_args()
    reader = fm.FORMATS[args.input_format][0]
    blocks = reader(args.platform, args.input, **args.reader_optargs)

    if args.output is not None:
        writer = fm.FORMATS[args.output_format][1]
        writer(args.platform, blocks, args.output)
        #   XXX relies on exit() to close files
