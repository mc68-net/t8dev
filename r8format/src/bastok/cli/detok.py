#!/usr/bin/env python3

from    argparse  import ArgumentParser
import  sys

from    bastok.tlines import TLines
from    bastok.detok.msx2 import Detokenizer
from    bastok.charset.msx import CHARMAP

def die(exitcode, *msglines):
    for l in msglines:
        print(l, file=sys.stderr)
    exit(exitcode)

def parseargs(argv1):   # `None` to use `sys.argv[1:]`
    p = ArgumentParser(description='MSX-BASIC detokenizer')
    arg = p.add_argument

    arg('-b', '--binary', action='store_true',
        help='do not do charset conversion (implies --dos-text)')
    arg('-c', '--charset', default='ja',
        help='MSX charset: ja (default), int, ar, ru, etc.')
    arg('-e', '--expand', action='store_true',
        help='add spaces for readability')
    arg('-z', '--dos-text', action='store_true',
        help='Use DOS textfile format (CR+LF EOL, ^Z at EOF)')
    arg('input', help='input file (required); use `-` for stdin')

    return p.parse_args(argv1)

def main(*, argv1=None, input_override=None):
    args = parseargs(argv1)

    if args.expand and args.binary:
        die(2, '--binary and --expand are incompatible')

    if args.binary:
        cmap = None
        args.dos_text = True
    else:
        cmap = CHARMAP.get(args.charset)
        if cmap is None:
            die(3, 'Unknown MSX charset: {}'.format(args.charset),
                'Known charsets:',
                *[ ' {:>4}: {}'.format(k, v.description)
                   for k, v in sorted(CHARMAP.items()) ]
                )

    if input_override is not None:
        f = input_override
    elif args.input == '-':
        f = sys.stdin.buffer
    else:
        try:
            f = open(args.input, 'rb')
        except FileNotFoundError as ex:
            print(str(ex))
            sys.exit(1)

    type = f.read(1)[0]
    if type != 0xFF:
        raise RuntimeError('bad type byte ${:02X}'.format(type))
    tl = TLines(f.read(), txttab=0x8001)  # XXX txttab should not be hard-coded
    f.close()

    #   We always write in binary mode, printing `str` output explictly
    #   as UTF-8 rather than letting the locale decide.
    out = sys.stdout.buffer
    endline = b'\n';
    if args.dos_text: endline = b'\r\n'
    for lineno, tline in tl.lines():
        detok = Detokenizer(cmap, tline, lineno, expand=args.expand)
        line = detok.detokenized()
        if not args.binary:
            line = bytes(line, 'UTF-8')
        out.write(line)
        out.write(endline)
    if args.dos_text:
        out.write(b'\x1A')
