''' cli.t8dev build commands

    The arguments to these vary by build command and may be passed via a
    command line, so for all of these the sole parameter is a list of
    arguments that the build function parses itself.
'''

from    pathlib  import Path
import  shutil

from    t8dev  import path
from    t8dev.cli.t8dev.asl   import asl1
from    t8dev.cli.t8dev.shared  import vprint
import  t8dev.run as run

####################################################################
#   Object File Transformation Tools
#
#   XXX These currently may call build tools such as asl1(); it's
#   not clear if or how those parts should be separated out.

def setargs_a2dsk(subparser):
    #   XXX this should probably be smaller steps with params divided up.
    a = subparser.add_parser('a2dsk',
        help='build Apple II disk image from ASL source file')
    a.set_defaults(func=a2dsk)
    a.add_argument('srcfile', help='file to assemble and put on to disk')

def a2dsk(args):
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

    srcfile = args.srcfile
    vprint(1, '───── a2dsk', srcfile)
    vprint(3, 'argparse', args)

    #   XXX srcfile = path.proj(srcfile) breaks; this needs to be fixed
    a2name = Path(srcfile).stem.upper()

    def binfile(ext=''):
        return str(path.obj(srcfile).with_suffix(ext))

    #   Generate an Apple II 'B' file (machine language program)
    asl1(srcfile)
    run.tool('p2a2bin', binfile('.p'), stdout_path=binfile())

    #   Generate the Applesoft BASIC HELLO program to run the above.
    bootprog = '10 PRINT CHR$(4);"BRUN {}"'.format(a2name).encode('ASCII')
    run.tool('tokenize_asoft', input=bootprog, stdout_path=binfile('.HELLO'))

    #   Build a disk image with the above and a HELLO that willl run it.
    baseimg = path.tool('src/osimg/a2/EMPTY-DOS33-48K-V254.dsk')
    img     = binfile('.dsk')
    shutil.copyfile(str(baseimg), str(img))
    def dos33(*command):
        run.tool('dos33', '-y', str(img), *command)
    dos33('SAVE', 'B', binfile(), a2name)
    dos33('DELETE', 'HELLO')    # Avoids annoying SAVE overwrite warning.
    dos33('SAVE', 'A', binfile('.HELLO'), 'HELLO')
    #   Seems not required, but make sure HELLO is run on boot anyway.
    dos33('HELLO', 'HELLO')
