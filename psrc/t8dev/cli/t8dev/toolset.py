#   We do not import t8dev.toolset here because it has a dependency on
#   `requests`, which package should be optional for those not using
#   the toolset download/install/build part of t8dev.
from    t8dev  import path

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
    assert len(args) == 1, "buildtool() requires an argument"
    tsname = args.pop(0)
    from t8dev  import toolset
    tool_class = toolset.TOOLSETS[tsname]
    tool_class().main()

