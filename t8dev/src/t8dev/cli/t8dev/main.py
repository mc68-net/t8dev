''' cli.t8dev argument parsing and top level '''

from    argparse  import ArgumentParser
from    pathlib  import Path
from    site  import addsitedir
import  os, sys

from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint
import  t8dev.cli.t8dev.shared as shared

from    t8dev.cli.t8dev.toolset     import setargs_toolset
from    t8dev.cli.t8dev.asl         import setargs_asl
from    t8dev.cli.t8dev.asx         import setargs_asx
from    t8dev.cli.t8dev.pytest      import setargs_pytest
from    t8dev.cli.t8dev.build       import setargs_a2dsk
from    t8dev.cli.t8dev.emulator    import setargs_emulator

def parseargs():
    ''' Parse arguments. If any of the arguments generate help messages,
        this will also exit with an appropriate code.
    '''
    ptop = ArgumentParser(description=
        'Tool to build toolsets and code for 8-bit development.')
    a = ptop.add_argument
    a('-P', '--project-dir',
        help='project directory; overrides T8_PROJDIR env var')
    a('-v', '--verbose', action='count', default=0,
        help='increase verbosity; may be used multiple times')

    command_group = ptop.add_subparsers(dest='command',
        # We do not use required=True; see below
        title='Subcommands', metavar='', help='')
    setargs_toolset(command_group)
    setargs_asx(command_group)
    setargs_asl(command_group)
    setargs_pytest(command_group)
    setargs_a2dsk(command_group)
    setargs_emulator(command_group)

    #   XXX Without a subcommand, this produces a poor error message:
    #   't8dev: error: the following arguments are required:' (with nothing
    #   after that). Ideally we should print the top-level help message as
    #   produced by ptop.format_help(), or at least say we need a
    #   subcommand and print a list of subcommands. It's not clear how to
    #   do that without some messy catching of SystemExit from
    #   ptop.parse_args().

    args = ptop.parse_args()
    if not args.command:
        cmd = Path(sys.argv[0]).name
        print( f'{cmd}: subcommand required; use -h for help', file=sys.stderr)
        #   We don't print the help here because it's rather verbose.
        exit(2)
    return args

def main():
    args = shared.ARGS = parseargs()

    if args.project_dir:    # override environment
        path.T8_PROJDIR = path.strict_resolve(args.project_dir)
    if path.T8_PROJDIR is None:
        raise RuntimeError('T8_PROJDIR not set')
    os.environ['T8_PROJDIR'] = str(path.T8_PROJDIR)
    vprint(1, f'━━━━━━━━ t8dev', args.command)
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
    exit(args.func(args))
