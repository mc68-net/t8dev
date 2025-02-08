''' cli.t8dev.isa XXX
'''

#   XXX This is not even used yet, perhaps because we're not doing as much
#   discovery of what to build as we should be? Though I (cjs) was sure we
#   were using it somewhere at some point, since I added the `.i80`
#   extension relatively recently.

from    collections  import namedtuple as ntup

ISA = ntup('ISA', 'cpu, stdinc')
ISAMAP = {
    '.a65': ISA('6502', 'mos65/std.a65'),
    '.a68': ISA('6800', 'mc68/std.a68'),
    '.i80': ISA('8080', 'i80/std.i80'),
}

#   XXX this should have a unit test
#   XXX and this isn't even used? (yet?)
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
