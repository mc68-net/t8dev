'''
    mb6885 - load an AS .p file into the bm2 simulator and run it

    The ``.p`` extension is added if missing, and if given a file name with
    no path (no slashes) it asssumes the file resides under
    ``.build/obj/exe/mb6885/``.
'''

from    sys  import argv, stderr

from    t8dev  import path
from    t8dev.cli  import exits
from    t8dev.run  import tool

def binname(fname):
    #   XXX similar to the testmc.tmc one; these need to be merged and pulled up
    if '.' not in fname: fname += '.p'
    if '/' not in fname: fname = path.obj('exe', 'mb6885', fname)
    return fname

def gen_srec(p_file):
    srec_file = p_file.with_suffix('.srec')
    tool('p2hex', p_file, srec_file, '-quiet')
    return srec_file

def runbm2(rom_dir=None, srec_file=None, entrypoint=None):
    ''' Run the bm2 emulator.

        `rom_dir` specifies the directory with ``{bas,prt,mon}.rom``.
        If `None`, no ROMs will be loaded (the built-in ROM emulation
        will be used).

        `srec_file`, if not `None`, is a path to a Motorola S-record
        file to be loaded into memory before the system resets.

        If `rom_dir` is `None`, `entrypoint` may be specified as the
        address to be placed in the reset vector before reset. (This
        is ignored if `rom_dir` is specified.)
    '''
    args = []
    if rom_dir is not None:
        args.append('-rom_dir=' + rom_dir)
    if srec_file is not None:
        args.append(str(srec_file))
        if entrypoint is not None:
            args.append(str(entrypoint))
    tool('bm2', *args)

def parseargs(args):
    rom_dir = str(path.tool('src', 'osimg', 'mb6885'))
    if len(args) > 0 and args[0] == '-n':     # no ROM
        rom_dir = None
        args.pop(0)

    srec_file = None
    if len(args) > 0:
        p_file = binname(args[0])
        srec_file = gen_srec(p_file)
        print(path.pretty(srec_file))
        args.pop(0)

    if len(args) > 0:
        exits.usage('mb6885 [-n] <file.p>')

    #   XXX HACK: we should be extracting this from srec_file.
    entrypoint = 0x3000

    return rom_dir, srec_file, entrypoint

def main():
    runbm2(*parseargs(argv[1:]))
