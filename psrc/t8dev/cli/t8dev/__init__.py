#!/usr/bin/env python3
'''
    t8dev - build tool for retro 8-bit cross-development

    The t8dev directory may be placed anywhere; ``t8dev`` uses its own
    path to find its modules. See the `t8dev.path` module documentation
    for information about the project directory structure and how the
    ``T8_PROJDIR`` environment variable is used. In particular, t8dev will
    always use tools from `path.tooldir('bin/')`, if available, in
    preference to any others.

    TODO:
    • t8dev should build project project-local tools into
      ``BASEDIR/.build/tool/``.

'''

# N.B. for developers:
# • In the long run we want nicer error messages, but for the moment
#   developers can easily enough work out the problem from the exception.
# • Older systems still supply Python 3.5. To try to remain compatible,
#   always use str() when passing path-like objects to standard library
#   functions.

from    collections  import namedtuple as ntup

from    t8dev.cli.t8dev.main  import main

####################################################################
#   t8dev Conventions

ISA = ntup('ISA', 'cpu, stdinc')
ISAMAP = {
    '.a65': ISA('6502', 'mos65/std.a65'),
    '.a68': ISA('6800', 'mc68/std.a68'),
    '.i80': ISA('8080', 'i80/std.i80'),
}

#   XXX this should have a unit test
#   XXX and this isn't even used? (yet?)
def isa_from_path(path, return_none=False):
    ''' Given a path, determine the instruction set architecture (ISA) from
        the filename's extension.

        The returned `ISA` object includes the lowest-common-denominator
        CPU type and the standard include file. The CPU type may be
        overridden by code that wants to use extended features of specific
        CPUs in that ISA (e.g., 65C02 for the 6502 ISA), but the file
        extensions do not determine things with that level of granularity.

        If `return_none` is `True`, `None` will be returned if the ISA
        cannot be determined. Otherwise a `LookupError` will be thrown with
        a message giving the unknown filename extension.
    '''
    _, ext = os.path.splitext(str(path))
    isa = ISAMAP.get(ext)
    if return_none or isa is not None:
        return isa
    else:
        raise LookupError("No ISA known for extension '{}'".format(ext))
