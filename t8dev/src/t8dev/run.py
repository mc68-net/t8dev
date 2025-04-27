' t8dev.run - Run and control subprocesses '

import  os, subprocess
from    itertools  import chain
from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint

def tool(toolbin, *args, errexit=True, input=None, stdout_path=None,
    envupdate=None, is32bit=False):
    ''' Run `toolbin` with the given `args`. On success this simply
        returns; on failure it prints the command line and the exit code
        and then exits this program. (This makes error output more readable
        than if a Python exception is thrown and printed.)

        `input` is passed directly to `subprocess.run()` and is typically
        a byte string.

        If `stdout_path` is given, that file will be opened in binary mode
        (creating it if necessary) and the standard output of the program
        will be written to it. (No output will produce an empty file.)

        If `envupdate` is set, it must be a mapping of names to values.
        The process will be run with an enivronment modified to have
        the given names set to the values.

        For tools that under Linux are 32-bit binaries, set `is32bit` to
        `True` to have a helpful message printed when the exit code is 127,
        usually indicating that support for running 32-bit binaries is not
        installed.
    '''
    vprint(2, 'run.tool',
        ' '.join(map(path.pretty, (chain([str(toolbin)], args)))))

    #   Relative `toolbin` uses explict path to project tool, if available.
    t8dev = path.tool('bin', toolbin)
    if os.access(str(t8dev), os.X_OK):
        toolbin = t8dev
    cmdline = ' '.join(map(path.pretty, [toolbin, *args]))

    runargs = (str(toolbin),) + tuple(map(str, args))
    try:
        if stdout_path is None:
            ret = subprocess.run(runargs, input=input, env=newenv(envupdate))
        else:
            with open(str(stdout_path), 'wb') as f:
                ret = subprocess.run(runargs, input=input, stdout=f,
                    env=newenv(envupdate))
        exitcode = ret.returncode
    except FileNotFoundError:
        print(f'FAILED: Executable {toolbin} not found for: {cmdline}')
        exit(127)

    if exitcode == 0:  return 0
    print(f'FAILED (exit={exitcode}): {cmdline}')
    if is32bit and exitcode == 127:
        print('(Do you support 32-bit executables?)', file=sys.stderr)
    if errexit:  exit(exitcode)
    return exitcode

def newenv(updates):
    ''' Return a copy of the environment mapping updated with all key/value
        pairs from the mapping `updates`. If `updates` is `None` an
        unmodified copy of the environment is returned.
    '''
    env = os.environ.copy()
    if updates is None:  return env
    for k, v in updates.items():  env[k] = v
    return env
