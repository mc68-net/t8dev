''' cli.t8dev commands for testing and execution of programs under test
'''

from    t8dev  import path

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

    non_opt_args = [ a for a in args if not a.startswith('-') ]
    args = [
        '--rootdir=' + str(path.proj()),
        '--override-ini=cache_dir=' + str(path.build('pytest/cache')),
        '-q',    # quiet by default; user undoes this with first -v
    ] + args + ( [] if non_opt_args else default_discovery_dirs )
    from pytest import main
    return(main(args))

