''' Fairly generic "utility" routines for cli.t8dev.
    These are used by a number of different modules.
'''

from    contextlib  import contextmanager
from    itertools  import chain
from    pathlib  import Path
from    sys import stderr
import  importlib.util, importlib.machinery, os

from    t8dev  import path, run
import  t8dev.cli.t8dev.shared as shared

def err(*msgs, exitcode=1):
    for msg in msgs:  print(msg, file=stderr)
    exit(exitcode)

def vprint(verbosity, prefix, *args, **kwargs):
    ''' Print for a given verbosity level.

        The message will be emitted only if `shared.ARGS.verbose` is at
        least as large as the `verbosity` argument.

        `prefix` is printed right-justified in a fixed-width field,
        followed by a colon and the message in `args`. This helps commands
        and the like line up nicely to make scanning through the output
        easier.
    '''
    if verbosity <= shared.ARGS.verbose:
        print('{:>8}:'.format(prefix), *args, **kwargs)

@contextmanager
def cwd(target):
    ''' Change the current working directory to `target` for the duration of
        the context, switching to the previous CWD when done. Non-existent
        directories will be created.

        To help debug problems, the CWD will be printed to stderr if any
        exception is raised. (The exception will be re-raised after
        printing.) This is a hack; the caller should control all printing.
    '''
    if not isinstance(target, Path):
        target = Path(target)
    oldcwd = Path.cwd()
    target.mkdir(parents=True, exist_ok=True)
    vprint(2, 'chdir', str(target))
    os.chdir(str(target))
    try:
        yield
    except BaseException:
        #   XXX Printing here is a hack (see docstring.)
        #   We catch BaseException to ensure that we print this even if
        #   the program is, e.g., trying to exit with a SystemExit.
        print('Exception with CWD', path.pretty(str(target)), file=stderr)
        raise
    finally:
        os.chdir(str(oldcwd))

def runtool(toolbin, *args, **kwargs):
    vprint(2, 'exec', ' '.join(chain([str(toolbin)], args)))
    run.tool(toolbin, *args, **kwargs)

SANDBOX_MODULES = {}
def sandbox_loadmod(modpath):
    ''' Load `modpath` as a Python module and return it, but without
        entering it into `sys.modules`. This is usually used for retrieving
        values from test modules without having to figure out where they
        might be integrated into the module hierarchy.

        The loaded modules are cached with key `modpath` to re-running
        them every time they are needed.

        Modules that throw exceptions will abort the interpreter, as any
        other code would. However, as special support for modules that use
        ``pytest.skip(..., allow_module_level=True)``, if an exception is
        thrown and its type name includes ``Skipped``, we do not raise the
        exception and abort but instead carry on. (The module will be
        evaluated up to that point.)
    '''
    #   We do our own caching instead of using functools.lru_cache so that
    #   we set the key and log cache hits.
    cache_key = path.pretty(modpath)
    vprint(1, 'loadmod', 'path={}'.format(cache_key))

    module = SANDBOX_MODULES.get(cache_key)
    if module:
        vprint(2, 'loadmod', '{} from cache'.format(module.__name__))
        return module

    #   The module name is used only for debugging, so make it simple.
    modname = str(Path(modpath).name).translate(str.maketrans('.', '_'))
    vprint(2, 'loadmod', 'loading as {}'.format(modname))
    loader = importlib.machinery.SourceFileLoader(modname, str(modpath))
    spec = importlib.util.spec_from_file_location(
        modname, str(modpath), loader=loader)
    if spec is None:
        #   This should never happen; if it does most likely we mucked up
        #   our loader setup or something like that.
        raise ImportError(
            "Can't create spec for module %s at location %s" % (modname, path))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except BaseException as ex:
        vprint(2, 'loadmod', 'module exec exception={} {}' \
            .format(type(ex), getattr(ex, 'msg', '<no `msg` attribute>')))
        if 'Skipped' in str(type(ex)):  # hack for pytest module skips
            vprint(2, 'loadmod', 'pytest `Skipped`')
        else:
            raise
    SANDBOX_MODULES[cache_key] = module
    return module

def remove_formfeeds(filepath):
    ''' Replace all form feeds with newlines in `filepath`. This makes
        listings cleaner when viewed on the screen.

        For ASXXXX .lst files, this must be done only *after* the .rst file
        is created by the linker because otherwise the extra newlines make
        the linker edit the wrong lines in the .lst file.
    '''
    f = Path(filepath)
    f.write_text(f.read_text().replace('\f', '\n'))

