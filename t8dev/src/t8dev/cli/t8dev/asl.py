' cli.t8dev ASL assembler commands '

from    itertools  import chain
from    pathlib  import Path
from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint
from    t8dev.cli.t8dev.util  import cwd, sandbox_loadmod, vprint
import  t8dev.run as run

def setargs_asl(subparser):
    parser = subparser.add_parser('asl',
        help='ASL (Macroassembler AS) commands ')
    spgroup = parser.add_subparsers(dest='subcommand', required=True,
        title='asl subcommands', metavar='', help='')

    a = spgroup.add_parser('asm', help='assemble files')
    a.set_defaults(func=asl)
    a.add_argument('file', nargs='+', help='file to assemble')

    t = spgroup.add_parser('t8dev',
        help='build all .asm files included with t8dev.')
    t.set_defaults(func=aslt8dev)

    m = spgroup.add_parser('auto', help='discover and build all files '
        'used by unit tests (`object_files`/`test_rig`)')
    m.set_defaults(func=aslauto)
    m.add_argument('-E', '--exclude', default=[], action='append',
        help='exclude these files/dirs (can be specified multiple times)')
    m.add_argument('path', nargs='+',
        help='path under which to search for unit tests')

    r = spgroup.add_parser('testrig', aliases=['tr'], help='create and build '
        'source for a pytest module containing a `test_rig`')
    r.add_argument('file', help='.pt file containing a `test_rig`')
    r.set_defaults(func=asltestrig)

def aslt8dev(args):
    ' Build all .asm files included with t8dev. '
    for dir in path.t8srcs():
        for file in dir.glob('**/*.asm'):
            relpath = file.relative_to(dir.parent)
            asl1(relpath)

def aslauto(args):
    ''' Auto-discover and build ASL source files and test rigs used by
        ``.pt`` files under `paths`, except for those under sub-paths
        excluded with the ``--exclude`` option.

        ``.pt`` files will be loaded as Python modules and the final value
        of the following global variables will be used to build sources
        in one of two ways:
        * ``object_files``: Any one file with the same path and basename
          with any extension other than ``.pt`` is considered to be the
          source file and assembled with `asl1()`. If multiple non-``*.pt``
          files exist or no other file exists, an error will be generated.
        * ``test_rig``: The `asl_testrig()` function will be called to
          create a source file containing the code in the ``test_rig``
          attribute and assemble it.

        XXX make this work for individual files
    '''
    if not args.path:
        args.path = ('src',)

    excludes_parts = tuple( path.proj(e).parts for e in args.exclude )
    def is_excluded(f):
        for e in excludes_parts:
            if e == f.parts[0:len(e)]:
                vprint(1, 'build', 'excluded: {}'.format(path.pretty(f)))
                return True
        return False

    object_files = set()
    testrig_files = set()
    ptfiles = chain(*[ path.proj(p).rglob('*.pt') for p in args.path ])
    for f in ptfiles:
        excluded = False
        if is_excluded(f): continue
        mod = sandbox_loadmod(f)
        if hasattr(mod, 'test_rig'):
            testrig_files.add(f)
        if hasattr(mod, 'object_files'):
            of = getattr(mod, 'object_files', None)
            if isinstance(of, str):   # see conftest.py
                object_files.add(of)
            else:
                object_files.update(of)

    #   For each test module with `object_files`, build the object files.
    for obj in sorted(object_files):
        stem = Path(obj).stem
        srcs = tuple(path.proj(obj).parent.glob(stem + '.*'))
        #   Remove .pt file from list of files we're considering.
        srcs = tuple(p for p in srcs if p.suffix != '.pt')
        prettysrcs = list(map(path.pretty, srcs))   # list prints nicer
        vprint(2, 'build', 'asl obj={} srcs={}'.format(obj, prettysrcs))
        #   In theory we could build several `srcs` with the same name but
        #   different extensions; in practice we don't support that due to
        #   output file name collisions.
        if len(srcs) == 1:
            asl1(srcs[0])
        else:
            raise RuntimeError('Cannot find source for {} in {}' \
                .format(obj, prettysrcs))

    #   For each test module with a `test_rig`, create the source file and
    #   build it.
    for pt in sorted(testrig_files):
        vprint(2, 'build', 'asl_testrig {}'.format(path.pretty(pt)))
        asl_testrig_file(pt)

def runasl(objdir, source:Path, sourcecode):
    ''' Create `objdir` and a source file in it named based on `source`
        contianing `sourcecode`, and assemble it with Macroassembler AS
        (``asl``).

        Only the `Path.stem` of source will be used (any path prefix and
        extension will be ignored) to give a file with the base name plus
        an ``.asm`` extension. however, if the assembly fails, the
        full `source` will be printed to indicate whence the assembly
        file used here was generated.

        ASL generates some output files (e.g., debug symbols) only to the
        current working directory, and only if the source file is in the
        current directory. (Included files may come from other
        directories.) Thus this function sets up the environment to
        assemble properly, including:
        - adding `path.proj()` to the assembler's include search path
        - using case-sensitive symbols
        - setting UTF-8 input
        - disabling listing pagination (the formfeeds and extra spacing are
          just irritating when viewing a listing file on screen)

        `sourcode` is assumed to have ``include`` statements that bring in
        the "real" source code to be assembled. (These would normally be
        paths relative to $T8_PROJDIR.) Conveniently, it may also include
        things like test rig setup if the source code is assembling a test
        rig to be unit-tested.
    '''
    vprint(1, 'runasl',
        f'source={path.pretty(source)} objdir={path.pretty(objdir)}')

    opts = [
        '-codepage', 'utf-8',
        '-qxx',
        '-U',                   # Case-sensitive symbols. This can be set
                                # only with a command-line option.
        '-i', str(path.proj()),
        '-i', str(path.t8include()),
        ]
    endopts = [ '-L', '-s', '-g', ]

    srcfile = source.stem + '.asm'
    with cwd(objdir):
        #   We always use Unix newline format for consistency across platforms.
        #   (Every decent editor for programmers handles this, and many people
        #   do this for all their source code.)
        with open(srcfile, 'w', newline='\n') as f:
            f.write('    page 0\n')                     # Disable pagination
            f.write(sourcecode)
        ec = run.tool('asl', *opts, srcfile, *endopts, errexit=False)
        if ec != 0:
            print(f'runasl assembly FAILED: {source}')
            exit(ec)

def asl(args):
    ' Call `asl1()` on each file. '
    for src in args.file: asl1(src)

def asl1(src):
    ''' Given a path to an assembler source file relative to `path.proj()`,
        generate an equivalent directory and under `path.obj()`, and invoke
        `runasl()` on a generated source file that includes the one given.

        This works around various issues with ASL input and output file
        locations. See `runasl()` for details.
    '''
    rsrc    = path.relproj(src)     # Used for assembler `include`
    src     = path.proj(rsrc)
    objdir  = path.obj(rsrc.parent)
    objfile = objdir.joinpath(rsrc.name).with_suffix('.p')

    vprint(1, '───── asl', src)
    vprint(3, 'rsrc', path.pretty(rsrc))
    vprint(3, 'objfile:', path.pretty(objfile))

    runasl(objdir, rsrc, '    include "{}"\n'.format(rsrc))

def asltestrig(args):
    asl_testrig_file(args.file)

def asl_testrig_file(file):
    ''' Given a path to a Python file relative to T8_PROJDIR, build its
        corresponding assembly-lanugage unit test rig using the
        Macroassembler AS. The Python file will be loaded as a module and
        the string value of its ``test_rig`` global variable will be
        assembled. Typically this would contain, at a minimum, something
        along the lines of:

            cpu 6502
            include "src/some/library.a65"
            org $1000

        All build products will be placed under `path.ptobj()`, with the
        path under that parallel to the pytest file's path and basename
        relative to $T8_PROJDIR.

        Note that this simply builds the code under test; it does not
        actually run any tests.
    '''
    vprint(1, '───── testrig', file)
    ptfile_rel  = path.relproj(file)        # includes .pt extension
    ptfile      = path.proj(ptfile_rel)
    ptfname     = ptfile_rel.stem           # filename: no path, no extension
    objdir      = path.ptobj(ptfile_rel.parent)
    objfile     = objdir.joinpath(ptfname).with_suffix('.p')

    runasl(objdir, ptfile_rel, sandbox_loadmod(ptfile).test_rig)
