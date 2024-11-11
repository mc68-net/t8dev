from    pytest  import main as pytest_main
import  argparse

from    t8dev  import path
from    t8dev.cli.t8dev.util  import vprint

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

    #   XXX Thoughts on improvements to this:
    #   1. If there's a top-level pyproject.toml, use the config from that
    #      instead of defaulting to src/ etc.
    #   2. Look for pyproject.toml files below and just do src/ and psrc/
    #      subdirs of those.
    #
    #   As well as using src/ as a default directory in which to discover
    #   tests, we also want to discover tests in our submodules such as
    #   t8dev and r8format. Ideally this should be done by extracting the
    #   test paths from tool.pytest.ini_options.testpaths in any
    #   pyproject.toml files in this working copy, but that's a bit
    #   difficult. So for the moment we rely on the fact that t8dev and
    #   r8format put their code under a psrc/ or (deprecated) pylib/
    #   subdir, and we just add any of those we find.
    default_discovery_dirs = list(map(str, [
        *path.proj().glob('**/psrc/'),
        *path.proj().glob('**/pylib/'),
        path.proj('src/'),
        ]))

    non_opt_args = [ a for a in args.ptarg if not a.startswith('-') ]
    allargs = [
        '--rootdir=' + str(path.proj()),
        '--override-ini=cache_dir=' + str(path.build('pytest/cache')),
        '-q',    # quiet by default; user undoes this with first -v
    ] + args.ptarg + ( [] if non_opt_args else default_discovery_dirs )
    vprint(2, 'pytest args', allargs)
    return(pytest_main(allargs))
