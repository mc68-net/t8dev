''' Generate `Intel HEX`_ format recorders from a `MemImage`.

    .. _Intel HEX: https://en.wikipedia.org/wiki/Intel_HEX
'''

from    binary.memimage  import MemImage

EOFREC = b':00000001FF'
' The Intel HEX end of file record. '

def intelhex(mem:MemImage) -> [str]:
    ''' Return a `[str]` of `Intel HEX`_ records of the data in `mem`.
        The records will each contain 16 data bytes except for the
        last in any `MemImage.MemRecord` section which may contain less.

        No $01 (End of File) record will be generated; this allows you
        to concatenate other Intel HEX records to output of this.

        No extensions (e.g., to support entry points) are currently
        supported.

        This generates only type $00 records; addresses outside the
        $0000-$FFFF will cause an exception to be thrown.

        .. _Intel HEX: https://en.wikipedia.org/wiki/Intel_HEX
    '''
    hexrecs = []
    for mrec in mem:
        hexrecs.extend(_intelhexrecs(mrec))
    return hexrecs

def _intelhexrecs(mrec:MemImage.MemRecord) -> [str]:
    ''' Produce a list of Intel HEX records from a `MemImage.MemRecord`.
        All records, except for perhaps the last, will be 16 bytes
        in length.
    '''
    hexrecs = []
    for i in range(0, len(mrec.data), 16):
        rectype = 0x00
        addr = mrec.addr + i
        data = mrec.data[i:i+16]
        record = [
            len(data),
            (addr & 0xFF00) >> 8, addr & 0x00FF,
            rectype,
            *data,
            ]
        record.append(_checksum(record))
        hexrec = ':' + ''.join(f'{byte:02X}' for byte in record)
        hexrecs.append(bytes(hexrec, encoding='ASCII'))
    return hexrecs

def _checksum(ints:[int]):
    sum8 = sum(ints) % 0x100
    return (0x100 - sum8) % 0x100
