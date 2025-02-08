' Exit and error message routines '

from    sys  import stderr

def warn(*msgs):
    for msg in msgs:
        print(msg, file=stderr)

#   We don't use /usr/include/sysexits.h (with, e.g., EX_USAGE = 64)
#   because "2 for bad usage" etc. seems simpler.

def err(*msgs, exitcode=1):
    warn(*msgs)
    exit(exitcode)

def arg(*msgs):
    err(*msgs, 2)

def usage(usage):
    err('Usage: ' + usage)
