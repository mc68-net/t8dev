' Sharp MZ-80K/MZ700/??? CMT format. '

from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PulseDecoder, PULSE_MARK, PULSE_SPACE, \
        Encoder, silence, sound, ReadError
import  cmtconv.audio

####################################################################

class Block(object):
    ''' Sharp MZ tape block.

        It's not clear what machines this is good for, but it seems to be
        at least MZ-80K and MZ-700.

        There are only two types of tape blocks, header and file data. Only
        the former has any specific format.

        For more references on this, see:
        <https://gitlab.com/retroabandon/sharp-mz-re>
    '''

    platform = "Sharp MZ"

    class ChecksumError(ValueError) : pass

    def __repr__(self):
        return '{}.{}( data={})'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                self._data)

class FileBlock(Block):

    @classmethod
    def make_block(cls):
        return cls()

    @property
    def isoef(self):
        return True

    def setdata(self, data):
        self._data = data

    @property
    def filedata(self):
        return self._data

    def to_bytes(self):
        return self._data + bytes( (0x00, ) * 10 )

class HeaderBlock(Block):

    @classmethod
    def make_block(cls, file_name, file_type, load_addr, exec_addr, comment):
        return cls(file_name, file_type, load_addr, exec_addr, comment)

    @classmethod
    def from_header(cls, headerbytes):
        ' Parse an exactly 128 byte header and produce a `HeaderBlock`. '
        hblen = len(headerbytes)
        if hblen != 128:  raise ValueError('headerbytes len {hblen} ≠ 128')
        raise RuntimeError('XXX write me')

    def __init__(self, file_name=None, file_type=None, binary=None):
        ...

   #@property
   #def isoef(self):
   #    return True

   #def setdata(self, data):
   #    self._data = data

   #@property
   #def filedata(self):
   #    return self._data

   #def to_bytes(self):
   #    ...
