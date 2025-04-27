from    pytest  import main as pytest_main
from    pathlib  import Path
import  argparse

from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint

def setargs_pytest(subparser):
    ''' This generates a parser where all arguments, even options, are simply
        accepted rather than parsed, so that the user can give any old pytest
        options to be passed on to pytest. `argparse.REMAINDER` only partially
        works for this; it will ignore ``foo -q``, but not ``-q foo`` when
        what it thinks is an option comes before the (obviously non-option)
        ``args`` parameter. We work around this by setting the option prefix
        character to a high (and invalid) Unicode character that nobody is
        likely to enter.
    '''
    p = subparser.add_parser('pytest', aliases=['pt'],
        prefix_chars='\uFFEF',    # hack to get parser to ignore all options
        help='run pytest on given arguments')
    p.set_defaults(func=pytest)
    p.add_argument('ptarg', nargs=argparse.REMAINDER, help='pytest arguments')

def pytest(args):
    ''' Run pytest. This is not forked but done within this process, so it
        inherits the entire t8dev Python environment, including access to
        all modules provided by t8dev. It also, somewhat confusingly, means
        that pytest usage error messages give "t8dev" as the name of the
        program.

        This sets the pytest ``rootdir`` to $T8_PROJDIR. It does not use an
        INI file but instead specifies all configuration it needs as
        command-line options. This does enable the developer to use ini
        files if she wishes, but be warned this can be tricky. For example,
        ``testpaths`` is not usually useful because t8dev is designed to
        run independently of CWD, and so doesn't set it.
    '''
    #   Remember that pytest comes from the (virtual) environment in which
    #   this program is run; it's not a tool installed by this program.

    vprint(1, '━━━━━━━━ pytest')
    vprint(3, 'pytest subcommand', args)

    #   Discovery works slightly differently from default pytest in that by
    #   default we search from $T8_PROJDIR downward for tests, rather than
    #   the CWD, if no test files are supplied on the command line. (This
    #   is specified as a command line argument, and thus overrides
    #   configuration files.) Thus, specify `.` on the command line if you
    #   want the default pytest behaviour.
    #
    #   We determine if we've been given a path or file to search by
    #   checking for every argument to see if it exists in the filesystem
    #   (relative to CWD). This is an imperfect heuristic, but generally
    #   good enough.
    #
    #   If there's a top level pyproject.toml or similar config file, it
    #   would be nice to use the default configuration from that (as pytest
    #   uses it if CWD is the root dir), but that's a fair amount of extra
    #   work and it's not clear we would gain much from it. (And it still
    #   runs into the issue about what to do with subdirectory/submodule
    #   config files.

    path_args = [ arg for arg in args.ptarg if Path(arg).exists() ]
    allargs = [
        '--rootdir=' + str(path.proj()),
        '--override-ini=cache_dir=' + str(path.build('pytest/cache')),
        '-q',    # quiet by default; user undoes this with first -v
    ] + args.ptarg
    if not path_args: allargs.append(str(path.proj()))
    vprint(2, 'pytest args', allargs)
    return(pytest_main(allargs))
