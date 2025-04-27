' Vars etc. shared amongst all `t8dev` command line tool modules. '

ARGS = None

def vprint(verbosity, prefix, *args, **kwargs):
    ''' Print for a given verbosity level.

        The message will be emitted only if `shared.ARGS.verbose` is at
        least as large as the `verbosity` argument.

        `prefix` is printed right-justified in a fixed-width field,
        followed by a colon and the message in `args`. This helps commands
        and the like line up nicely to make scanning through the output
        easier.
    '''
    if verbosity <= ARGS.verbose:
        print('{:>8}:'.format(prefix), *args, **kwargs)
