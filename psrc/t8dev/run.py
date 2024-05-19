' t8dev.run - Run and control subprocesses '

import  os, subprocess
from    t8dev  import path

def tool(toolbin, *args, input=None, stdout_path=None, is32bit=False):
    ''' Run `toolbin` with the given `args`. On success this simply
        returns; on failure it prints the command line and the exit code
        and then exits this program. (This makes error output more readable
        than if a Python exception is thrown and printed.)

        `input` is passed directly to `subprocess.run()` and is typically
        a byte string.

        If `stdout_path` is given, that file will be opened in binary mode
        (creating it if necessary) and the standard output of the program
        will be written to it. (No output will produce an empty file.)

        For tools that under Linux are 32-bit binaries, set `is32bit` to
        `True` to have a helpful message printed when the exit code is 127,
        usually indicating that support for running 32-bit binaries is not
        installed.
    '''
    #   Relative `toolbin` uses explict path to project tool, if available.
    t8dev = path.tool('bin', toolbin)
    if os.access(str(t8dev), os.X_OK):
        toolbin = t8dev
    cmdline = ' '.join(map(path.pretty, [toolbin, *args]))

    runargs = (str(toolbin),) + tuple(map(str, args))
    try:
        if stdout_path is None:
            ret = subprocess.run(runargs, input=input)
        else:
            with open(str(stdout_path), 'wb') as f:
                ret = subprocess.run(runargs, input=input, stdout=f)
        exitcode = ret.returncode
    except FileNotFoundError:
        print(f'FAILED: Executable {toolbin} not found for: {cmdline}')
        exit(127)

    if exitcode == 0:  return
    print(f'FAILED (exit={exitcode}): {cmdline}')
    if is32bit and exitcode == 127:
        print('(Do you support 32-bit executables?)', file=sys.stderr)
    exit(exitcode)
