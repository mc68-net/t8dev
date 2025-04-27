#   We do not import t8dev.toolset here because it has a dependency on
#   `requests`, which package should be optional for those not using
#   the toolset download/install/build part of t8dev.
from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint
from    t8dev.cli import exits

def setargs_toolset(subparser):
    p = subparser.add_parser('toolset', aliases=['tool', 'ts'],
        help='confirm or build development toolsets',
        description='Confirm or build a development toolset. '
            ' This will first see if the toolset is already available by'
            ' attempting to to run the tool or otherwise confirm its presence.'
            ' If not present, it will download, build and isntall the toolset'
            ' under the $BUILD/tool/ directory.'
        )
    p.set_defaults(func=buildtoolset)
    a = p.add_argument
    a('-f', '--force-build', action='store_true',
        help='build toolset even if already available')
    a('name', nargs='+',
        help="name of toolsets confirm/build, or 'list' available toolsets")

def buildtoolsets(args):
    ''' This should check the configuration of the project and build
        all tools that have been enabled (or at least confirm that
        they are available from the system).

        XXX WRITEME
    '''
    raise NotImplementedError('XXX writeme')

def buildtoolset(args):
    ''' Given the name of a toolset, run its setup/build/install code.

        This will first check to see if the toolset is already available in
        the current path and do nothing if it is. Otherwise it will fetch,
        build and install the toolset to the project's local tool directories.

        XXX There should really be an option to force building a
        project-local toolset even when the system provides one.
    '''
    if args.force_build:
        exits.err(11, 't8dev toolset: --force-build not yet implmented')

    from t8dev.toolset import TOOLSETS
    if args.name[0] == 'list':
        print(f'Toolsets: ', ' '.join(TOOLSETS))
        exit(0)
    for ts in args.name:
        vprint(1, '━━━━━━━━ toolset', ts)
        tool_class = TOOLSETS.get(ts)
        if tool_class is None:
            exits.err(1, f"Cannot find toolset '{ts}'."
                " Use toolset 'list' to see available toolsets.")
        #   XXX toolset.Setup probably wants to drop main() and just use setup()
        #   XXX It's not clear if we want `force_build=True` to be an argument
        #   to __init__() or setup().
        tool_class().main()
