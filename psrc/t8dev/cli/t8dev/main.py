''' cli.t8dev argument parsing and top level '''

from    argparse  import ArgumentParser
from    site  import addsitedir
import  os, sys

from    t8dev.cli.t8dev.build  import *
from    t8dev.cli.t8dev.execute  import *
from    t8dev.cli.t8dev.toolset  import buildtoolsets, buildtoolset
from    t8dev.cli.t8dev.util  import vprint
import  t8dev.cli.t8dev.shared as shared

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
