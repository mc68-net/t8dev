#
#   ascii2a2t - convert ASCII file to Apple II text format
#
#   Sends output to stdout.
#

from    sys  import argv, stdout
from    os   import fdopen
from    t8dev.cli  import exits

NL = 10     # ASCII newline
CR = 13     # ASCII CR

def main():
    if len(argv) != 2:
        exits.usage('ascii2a2t FILE')

    output = fdopen(stdout.fileno(), 'wb')
    with open(argv[1], 'rb') as input:
        while True:
            b = input.read(1)
            if len(b) == 0:     break
            b = b[0]
            if b > 127:         exits.err(f'Bad ASCII char: {b}')
            if b == NL:         b = CR
            b |= 0x80           # set high bit for Apple
            output.write(bytes([b]))
    output.flush()
