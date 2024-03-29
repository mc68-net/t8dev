#
#   ascii2a2t - convert ASCII file to Apple II text format
#
#   Sends output to stdout.
#

from    sys  import argv, stderr, stdout
from    os   import fdopen

# /usr/include/sysexits.h
EX_USAGE    = 64
EX_DATAERR  = 65
EX_IOERR    = 74

NL = 10     # ASCII newline
CR = 13     # ASCII CR

def main():
    if len(argv) != 2:
        print('Usage: ascii2a2t FILE', file=stderr)
        exit(EX_USAGE)

    output = fdopen(stdout.fileno(), 'wb')
    with open(argv[1], 'rb') as input:
        while True:
            b = input.read(1)
            if len(b) == 0:
                break
            b = b[0]
            if b > 127:
                print('Bad ASCII char:', b, file=stderr)
                exit(EX_DATAERR)
            if b == NL:
                b = CR
            b |= 0x80           # set high bit for Apple
            output.write(bytes([b]))
    output.flush()
