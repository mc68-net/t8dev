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

from    argparse  import ArgumentParser
from    collections  import namedtuple as ntup
from    site  import addsitedir
import  os, sys

from    t8dev.cli.t8dev.build  import *
from    t8dev.cli.t8dev.execute  import *
from    t8dev.cli.t8dev.toolset  import buildtoolsets, buildtoolset
from    t8dev.cli.t8dev.util  import vprint
import  t8dev.cli.t8dev.shared as shared

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

####################################################################
#   Top Level (Main)

def parseargs():
    ''' Parse arguments. If any of the arguments generate help messages,
        this will also exit with an appropriate code.
    '''
    p = ArgumentParser(
        description='Tool to build toolsets and code for 8-bit development.')
    a = p.add_argument
    a('-E', '--exclude', default=[], action='append',
        help='for commands that do discovery, exclude these files/dirs'
             ' (can be specified multiple times)')
    a('--help-commands', action='store_true', help='print available commands')
    a('-P', '--project-dir',
        help='project directory; overrides T8_PROJDIR env var')
    a('-v', '--verbose', action='count', default=0,
        help='increase verbosity; may be used multiple times')
    a('command', nargs='?',
        help='command; --help-commands for a list')
    a('args', nargs='*',
        help="arguments to command (preceed with '--' to use args with '-')")

    args = p.parse_args()
    if args.help_commands:      help_commands(); exit(0)
    if args.command is None:    p.print_help(); exit(0)
    return args

def help_commands():
    print('{}: Command List'.format(sys.argv[0]))
    for c in sorted(COMMANDS):
        print('  {}'.format(c))

COMMANDS = {
    'asl':      asl,        # Assemble single program with Macroassembler AS
    'asltest':  asltest,    # Assemble single unit test with Macroassembler AS
    'aslauto':  aslauto,    # Discover and build all ASL stuff in given dirs
    'asx':      asx,        # ASXXXX assembler
    'asxlink':  asxlink,    # ASXXXX linker
    'a2dsk':    a2dsk,      # Apple II .dsk image that boots and runs program
    'bt':       buildtoolset,  'buildtoolset':  buildtoolset,
    'bts':      buildtoolsets, 'buildtoolsets': buildtoolsets,
    'pytest':   pytest,
}

def main():
    shared.ARGS = parseargs()

    if shared.ARGS.project_dir:    # override environment
        path.T8_PROJDIR = path.strict_resolve(shared.ARGS.project_dir)
    if path.T8_PROJDIR is None:
        raise RuntimeError('T8_PROJDIR not set')
    vprint(1, '========',
        't8dev command={} args={}'.format(shared.ARGS.command, shared.ARGS.args))
    vprint(1, 'projdir', str(path.proj()))

    #   Code common to several .pt files (including entire test suites) may
    #   be factored out into .py files that are imported by multiple .pt
    #   files. We add $T8_PROJDIR to the Python search path so that they
    #   can `import src.common` or similar, both when imported by asltest().
    #   and when imported by pytest. (Though pytest already provided this.)
    #
    #   XXX This probably also has implications for other things; we need
    #   to sit down and work out how we really want to deal with it.
    #
    addsitedir(str(path.proj()))

    cmdf = COMMANDS.get(shared.ARGS.command)
    if cmdf is None:
        help_commands(); exit(2)
    exit(cmdf(shared.ARGS.args))
