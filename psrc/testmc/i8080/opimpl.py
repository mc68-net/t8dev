''' Implementation of opcodes.
'''

#   XXX This contains a _lot_ of code copied from testmc.mc6800.opimpl;
#   the common code should be pulled up to testmc.generic.opimpl.

####################################################################

class InvalidOpcode(RuntimeError):
    ''' Since it is designed for testing code, the simulator
        will not execute invalid opcodes, instead raising an exception.
    '''
    def __init__(self, opcode, regs):
        self.opcode = opcode; self.regs = regs
        super().__init__('op=${:02X}, {}'.format(opcode, regs))

def invalid(m):
    #   The PC PC has already been advanced past the opcode; undo this.
    pc = incword(m.pc, -1)
    regs = m.regs.clone(pc=pc)
    raise InvalidOpcode(m.mem[pc], regs)

####################################################################
#   Address handling, reading data at the PC

def incbyte(byte, addend):
    ''' Return 8-bit `byte` incremented by `addend` (which may be negative).
        This returns an 8-bit unsigned result, wrapping at $FF/$00.
    '''
    return (byte + addend) & 0xFF

def incword(word, addend):
    ''' Return 16-bit `word` incremented by `addend` (which may be negative).
        This returns a 16-bit unsigned result, wrapping at $FFFF/$0000.
    '''
    return (word + addend) & 0xFFFF

def readbyte(m):
    ' Consume a byte at [PC] and return it. '
    val = m.byte(m.pc)
    m.pc = incword(m.pc, 1)
    return val

#   XXX endian?
def signedbyteat(m, addr):
    ' Return the byte at `addr` as a signed value. '
    return unpack('b', m.bytes(addr, 1))[0]

def readsignedbyte(m):
    ' Consume a byte at [PC] as a signed value and return it. '
    val = signedbyteat(m, m.pc)
    m.pc = incword(m.pc, 1)
    return val

def readword(m):
    ' Consume a word at [PC] and return it. '
    # Careful! PC may wrap between bytes.
    return (readbyte(m) << 8) | readbyte(m)

def readreloff(m):
    ''' Consume a signed relative offset byte at [PC] and return the
        target address. '''
    offset = readsignedbyte(m)
    return incword(m.pc, offset)

def readindex(m):
    ''' Consume an unsigned offset byte at [PC], add it to the X register
        contents and return the result.
    '''
    return incword(m.x, readbyte(m))

