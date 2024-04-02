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
    return readbyte(m) | (readbyte(m) << 8)

def readreloff(m):
    ''' Consume a signed relative offset byte at [PC] and return the
        target address. '''
    offset = readsignedbyte(m)
    return incword(m.pc, offset)

def readindex(m):
    ''' Consume an unsigned offset byte at [PC], add it to the X register
        contents and return the result.
    '''
    #   XXX 6800 has an X register, we don't!
    return incword(m.x, readbyte(m))

####################################################################
#   Instructions affecting the stack

def popbyte(m):
    ' Pop a byte off the stack and return it. '
    val = m.byte(m.sp)
    m.sp = incword(m.sp, 1)
    return val

def popword(m):
    ' Pop a word off the stack and return it. '
    lsb = popbyte(m)
    msb = popbyte(m)
    return (msb << 8) + lsb

def pushbyte(m, byte):
    ' Push a byte on to the stack. '
    m.sp = incword(m.sp, -1)
    m.deposit(m.sp, byte)

def pushword(m, word):
    ' Push a word on to the stack, MSB higher in memory than LSB. '
    pushbyte(m, word >> 8)
    pushbyte(m, word & 0xFF)

def ret(m):     m.pc = popword(m)

####################################################################
#   Instructions

def mvia(m):    m.a = readbyte(m)

def sta(m):     m.mem[readword(m)] = m.a

#   XXX how to parametrize this so as not to repeat it 64 times?
def movba(m):   m.b = m.a
def movca(m):   m.c = m.a
def movda(m):   raise NotImplementedError('XXX genericise this!')

####################################################################
#   Logic Functions

def iszero(b):
    return b == 0

def isneg(b):
    sign = b & (1 << 7)
    return 0 !=  sign

def parity(byte):
    #   _Hacker's Delight,_ 2nd ed, §5.2, p.100
    p = byte ^ (byte>>1)
    p = p ^ (p>>2)
    p = p ^ (p>>4)
    return not (p&1)

def logicSZP(m, val):
    ''' Set sign, zero and parity flags based on `val`.
        Clear carry and half (auxiliary) carry.
        This is used for logic operations.
    '''
    m.S = isneg(val)
    m.Z = iszero(val)
    m.P = parity(val)
    m.H = m.C = False
    return val

def xraa(m):    m.a = logicSZP(m, m.a ^ m.a)

