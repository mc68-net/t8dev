''' cli.t8dev build commands

    The arguments to these vary by build command and may be passed via a
    command line, so for all of these the sole parameter is a list of
    arguments that the build function parses itself.
'''

from    itertools  import chain
from    pathlib  import Path
import  shutil

from    t8dev.cli.t8dev.util  import *
from    t8dev  import path
import  t8dev.cli.t8dev.shared as shared

####################################################################
#   ASL Assembler

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
        '-i', str(path.t8include()),
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

    runasl(objdir, rsrc.stem, '    include "{}"\n'.format(rsrc))

def asl_testrig(args):
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
    if len(args) != 1:
        #   Can't think of any reason we'd ever want to supply > one arg.
        raise ValueError('asl_testrig takes only one arg')

    ptfile_rel  = path.relproj(args[0])     # includes .pt extension
    ptfile      = path.proj(ptfile_rel)
    ptfname     = ptfile_rel.stem           # filename: no path, no extension
    objdir      = path.ptobj(ptfile_rel.parent)
    objfile     = objdir.joinpath(ptfname).with_suffix('.p')

    runasl(objdir, ptfname, sandbox_loadmod(ptfile).test_rig)

def aslauto(paths):
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
    if not paths:
        paths = ('src',)

    excludes_parts = tuple( path.proj(e).parts for e in shared.ARGS.exclude )
    def is_excluded(f):
        for e in excludes_parts:
            if e == f.parts[0:len(e)]:
                vprint(1, 'build', 'excluded: {}'.format(path.pretty(f)))
                return True
        return False

    object_files = set()
    testrig_files = set()
    ptfiles = chain(*[ path.proj(p).rglob('*.pt') for p in paths ])
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
        asl_testrig([pt])

def aslt8dev(args):
    ' Build all .asm files included with t8dev. '
    if len(args) != 0:
        raise RuntimeError('len(args) != 0')

    for dir in path.t8srcs():
        for file in dir.glob('**/*.asm'):
            relpath = file.relative_to(dir.parent)
            asl1(relpath)


####################################################################
#   ASxxxx Assembler and Linker

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

####################################################################
#   Object File Transformation Tools
#
#   XXX These currently may call build tools such as asl1(); it's
#   not clear if or how those parts should be separated out.

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
    #   • The use of str(...) is annoying, perhaps we need some better
    #     general plan for handling paths. The main issue is that they
    #     currently usually come in as strings from command lines, but
    #     possibly Path objects from other code. (But also, do we even
    #     need str(...) if we no longer need Python 3.5 support?

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
