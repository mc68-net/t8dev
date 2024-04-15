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
from    itertools  import chain
from    pathlib  import Path
from    site  import addsitedir
import  os, shutil, sys

from    t8dev  import path
from    t8dev.cli.t8dev.toolset  import buildtoolsets, buildtoolset
from    t8dev.cli.t8dev.util  import vprint, cwd, runtool, sandbox_loadmod
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
#   Build commands
#
#   The arguments to these vary by build command and may be passed
#   via a command line, so for all of these the sole parameter is
#   a list of arguments that the build function parses itself.

def runasl(objdir, name, sourcecode):
    ''' Create `objdir`, a source file in it called `name`.asm containing
        `sourcecode`, and assemble it with Macroassembler AS (``asl``).

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
    vprint(1, 'runasl', 'name={} objdir={}'.format(name, path.pretty(objdir)))

    opts = [
        '-codepage', 'utf-8',
        '-qxx',
        '-U',                   # Case-sensitive symbols. This can be set
                                # only with a command-line option.
        '-i', str(path.proj()),
        ]
    endopts = [ '-L', '-s', '-g', ]

    srcfile = name + '.asm'
    with cwd(objdir):
        #   We always use Unix newline format for consistency across platforms.
        #   (Every decent editor for programmers handles this, and many people
        #   do this for all their source code.)
        with open(srcfile, 'w', newline='\n') as f:
            f.write('    page 0\n')                     # Disable pagination
            f.write(sourcecode)
        runtool('asl', *opts, srcfile, *endopts)

def asl(args):
    ' Call `asl1()` on each file in `args`. '
    for src in args: asl1(src)

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

    runasl(objdir, rsrc.stem, '    include "{}"'.format(rsrc))

def asltest(args):
    ''' Given a path to a pytest file realtive to T8_PROJDIR, build its
        corresponding assembly-lanugage unit test rig using the
        Macroassembler AS. The pytest file will be loaded as a module and
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
    if len(args) != 1:
        #   Can't think of any reason we'd ever want to supply > one arg.
        raise ValueError('asltest takes only one arg')

    ptfile_rel  = path.relproj(args[0])     # includes .pt extension
    ptfile      = path.proj(ptfile_rel)
    ptfname     = ptfile_rel.stem           # filename: no path, no extension
    objdir      = path.ptobj(ptfile_rel.parent)
    objfile     = objdir.joinpath(ptfname).with_suffix('.p')

    runasl(objdir, ptfname, sandbox_loadmod(ptfile).test_rig)

def aslauto(paths):
    ''' Auto-discover and build ASL source files used by ``.pt`` files
        under `paths`, except for those under sub-paths excluded with the
        ``--exclude`` option.

        ``.pt`` files will be loaded as Python modules and the final value
        of the following global variables will be used to build sources:
        * ``object_files``: Any one file with the same path and basename
          with any extension other than ``.pt`` is considered to be the
          source file and assembled with `asl1()`. If multiple non-``*.pt``
          files exist or no other file exists, an error will be generated.
        * ``test_rig``: An object file named for the `.pt` file will be
          generated using using the code in ``test_rig`` by calling
          `asltest()`.

        XXX make this work for individual files
    '''
    if not paths:
        paths = ('src',)

    excludes_parts = tuple( path.proj(e).parts for e in shared.ARGS.exclude )
    def is_excluded(f):
        for e in excludes_parts:
            if e == f.parts[0:len(e)]:
                vprint(1, 'build', 'excluded: {}'.format(path.pretty(f)))
                return True
        return False

    asl_files = set()
    asltest_files = set()
    ptfiles = chain(*[ path.proj(p).rglob('*.pt') for p in paths ])
    for f in ptfiles:
        excluded = False
        if is_excluded(f): continue
        mod = sandbox_loadmod(f)
        if hasattr(mod, 'test_rig'):
            asltest_files.add(f)
        if hasattr(mod, 'object_files'):
            of = getattr(mod, 'object_files', None)
            if isinstance(of, str):   # see conftest.py
                asl_files.add(of)
            else:
                asl_files.update(of)

    for obj in sorted(asl_files):
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

    for pt in sorted(asltest_files):
        vprint(2, 'build', 'asltest {}'.format(path.pretty(pt)))
        asltest([pt])

def asx(args):
    ''' Run ASXXXX assembler. Currently this always runs ``as6500``.

        `args[0]` is the source path, relative to `BASEDIR`.
        Any further arguments are passed as-is to the assembler.

        The assembly options we use are:
          -x  Output in hexadecimal
          -w  Wide listing format for symbol table
              (symbol name field 55 chars instead of 14)
          -p  Disable listing pagination
          -l  Create listing file (`.lst`)
          -o  Create object file (`.rel`)
          -s  Create symbol file (`.sym`) (removes symtab from listing file)
          -r  Inlcude assembler line numbers in the `.hlr` hint file
          -rr Inlcude non-list assembler line numbers in the `.hlr` hint file
          -f  Flag relocatable references with backtick in listing
    '''
    asmopts = '-xwplof'

    if len(args) != 1:
        raise RuntimeError('len(args) != 1')

    srcfile = path.proj(args[0])
    srcdir  = Path(args[0]).parent
    objdir  = path.obj(srcdir)
    objfile = objdir.joinpath(srcfile.stem)

    objdir.mkdir(parents=True, exist_ok=True)
    runtool('as6500', asmopts, str(objfile), str(srcfile), *args[2:])

def asxlink(args):
    ''' Link ASXXXX assembler output.

        `arg[0]` is the source path relative to `BASEDIR` (which will be
        translated to an object path) followed by the output file basename.
        Any extension will be removed; the output file will automatically
        have .hex/.s19/.bin appened to it. If no input filenames are given
        in additional arguments, the basename of this file plus ``.rel`` is
        the input file.

        `arg[1:]`, if present, are a mix of linker options and input
        filenames (with or without .rel extension). Input filenames
        are relative to the object dir of the output file. (Possibly
        they should instead take source dir paths; see the comments
        in the function for a discussion of this.)

        The link options we use are:
          -n  No echo of commands to stdout
          -u  Update listing file (.lst) with relocated addresses from .rst
              (This does not update the addresses in the symbol table.)
          -m  Generate map output file (`.map`)
          -w  "Wide" mode for map file (show 32 chars, not 8, of symbol names)
          -t  Output format: Tandy Color Computer BASIC binary file (`.bin`)
    '''
    linkopts="-numwt"

    srcpath = Path(args[0])
    srcdir = srcpath.parent
    objstem = srcpath.name      # possibly should remove .rel here, if present
    objdir = path.obj(srcdir)

    #   XXX We should use absolute paths rather than setting a CWD.
    #   However, this requires us to generate absolute paths for the file
    #   arguments to the linker, which probably requires us to specify
    #   those separately from the linker options if we're to do this
    #   reliably. (Otherwise we need to duplicate some of the linker's
    #   option parsing code.) The current behaviour isn't causing much
    #   pain, so this has not yet been fixed.
    with cwd(objdir):
        runtool('aslink', linkopts, objstem, *args[1:], is32bit=True)
        remove_formfeeds(objstem + '.lst')
        remove_formfeeds(objstem + '.rst')
        remove_formfeeds(objstem + '.map')

def a2dsk(args):
    ' Call `a2dsk1()` on each file in `args`. '
    for src in args: a2dsk1(src)

def a2dsk1(srcfile):
    ''' Assemble a program with Macroassembler AS and build a bootable
        Apple II ``.dsk`` image containing that program and a ``HELLO``
        that will run it. This calls `asl` to do the assembly; `args` will
        be passed to it unmodified.

        The program is typically run with something like::

            linapple --conf t8dev/share/linapple.conf \
                --d1 .build/obj/exe/a2/charset.dsk

        XXX We should work out an option to do this automatically.

        This requires dos33, mkdos33fs and tokenize_asoft from dos33fsprogs_,
        a base image from the retroabandon osimg_ repo, and the p2a2bin
        program.

        .. _dos33fsprogs: https://github.com/deater/dos33fsprogs.git
        .. _osimg: https://gitlab.com/retroabandon/osimg.git
    '''
    #   XXX and TODO:
    #   • t8dev should be handling the fetching and building of all
    #     these programs and template disk images.
    #   • p2a2bin is actually part of the `testmc` module; not sure
    #     whether that is part of t8dev or separate. (Does it want a
    #     proper Python package release, too?)
    #   • The use of str(...) is annoying, perhaps we need some better
    #     general plan for handling paths. The main issue is that they
    #     currently usually come in as strings from command lines, but
    #     possibly Path objects from other code.

    #   XXX srcfile = path.proj(srcfile) breaks; this needs to be fixed
    a2name = Path(srcfile).stem.upper()

    def binfile(ext=''):
        return str(path.obj(srcfile).with_suffix(ext))

    #   Generate an Apple II 'B' file (machine language program)
    asl1(srcfile)
    runtool('p2a2bin', binfile('.p'), stdout_path=binfile())

    #   Generate the Applesoft BASIC HELLO program to run the above.
    bootprog = '10 PRINT CHR$(4);"BRUN {}"'.format(a2name).encode('ASCII')
    runtool('tokenize_asoft', input=bootprog, stdout_path=binfile('.HELLO'))

    #   Build a disk image with the above and a HELLO that willl run it.
    baseimg = path.tool('src/osimg/a2/EMPTY-DOS33-48K-V254.dsk')
    img     = binfile('.dsk')
    shutil.copyfile(str(baseimg), str(img))
    def dos33(*command):
        runtool('dos33', '-y', str(img), *command)
    dos33('SAVE', 'B', binfile(), a2name)
    dos33('DELETE', 'HELLO')    # Avoids annoying SAVE overwrite warning.
    dos33('SAVE', 'A', binfile('.HELLO'), 'HELLO')
    #   Seems not required, but make sure HELLO is run on boot anyway.
    dos33('HELLO', 'HELLO')

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
