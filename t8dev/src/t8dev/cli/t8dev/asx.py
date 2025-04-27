'   ASxxxx Assembler and Linker '

from    pathlib  import Path
from    t8dev  import path
from    t8dev.cli.t8dev.shared  import vprint
from    t8dev.cli.t8dev.util  import cwd, remove_formfeeds, vprint
import  t8dev.run as run

def setargs_asx(subparser):
    parser = subparser.add_parser('asx',
        help='ASxxxx assembler and linker commands ')
    p = parser.add_subparsers(dest='subcommand', required=True,
        title='ASX subcommands', metavar='', help='')

    a = p.add_parser('asm',  help='assemble file with ASxxxx')
    a.set_defaults(func=asxasm)
    a.add_argument('file', help='file to assemble')

    l = p.add_parser('link',
        prefix_chars='\uFFEF',  # hack so argparse will not try to parse opts
        help='link assembler output files')
    l.set_defaults(func=asxlink)
    l.add_argument('basename', help='basename of module to link')
    l.add_argument('addargs', nargs='*',
        help='additional arguments to assembler')

def asxasm(args):
    ''' Run ASXXXX assembler. Currently this always runs ``as6500``.

        `args.file` is the source path, relative to `BASEDIR`.
        Currently no further arguments can be passed to the assembler.

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

    vprint(1, '────── asx asm', args.file)
    vprint(3, 'argeparse', args)
    srcfile = path.proj(args.file)
    srcdir  = Path(args.file).parent
    objdir  = path.obj(srcdir)
    objfile = objdir.joinpath(srcfile.stem)

    objdir.mkdir(parents=True, exist_ok=True)
    command_line = ('as6500', asmopts, str(objfile), str(srcfile))
    vprint(2, 'command line:', *command_line)
    run.tool(*command_line)

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
    vprint(1, '────── asx link', args.basename)
    vprint(3, 'argeparse', args)

    linkopts="-numwt"
    srcpath = Path(args.basename)
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
        run.tool('aslink', linkopts, objstem, *args.addargs, is32bit=True)
        remove_formfeeds(objstem + '.lst')
        remove_formfeeds(objstem + '.rst')
        remove_formfeeds(objstem + '.map')

