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
#   8-bit Register Move Instructions

def ld_rr(m, dst, src): setattr(m, dst, getattr(m, src))
def ld_ri(m, dst):      setattr(m, dst, readbyte(m))
def ld_mr(m, src):      m.mem[m.hl] = getattr(m, src)
def ld_rm(m, dst):      setattr(m, dst, m.mem[m.hl])

####################################################################
#   16-bit Instructions and Operands

def sta(m):             m.mem[readword(m)] = m.a

def inx_r(m, reg):       setattr(m, reg, incword(getattr(m, reg),  1))
def dcx_r(m, reg):       setattr(m, reg, incword(getattr(m, reg), -1))

def lxib(m):            m.bc = readword(m)
def lxid(m):            m.de = readword(m)
def lxih(m):            m.hl = readword(m)
def lxis(m):            m.sp = readword(m)

####################################################################
#   Logic Instructions

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

def and_r(m, reg):   m.a = logicSZP(m, m.a & getattr(m, reg))
def and_m(m):        m.a = logicSZP(m, m.a & m.mem[m.hl])
def and_i(m):       assert 0

def  or_r(m, reg):   m.a = logicSZP(m, m.a | getattr(m, reg))
def  or_m(m):        m.a = logicSZP(m, m.a | m.mem[m.hl])
def  or_i(m):       assert 0

def xor_r(m, reg):   m.a = logicSZP(m, m.a ^ getattr(m, reg))
def xor_m(m):        m.a = logicSZP(m, m.a ^ m.mem[m.hl])
def xor_i(m):       assert 0

####################################################################
#   Arithemetic Instructions

def add_r(m, reg):  assert 0
def add_m(m):       assert 0
def add_i(m):       assert 0

def adc_r(m, reg):  assert 0
def adc_m(m):       assert 0
def adc_i(m):       assert 0

def sub_r(m, reg):  assert 0
def sub_m(m):       assert 0
def sub_i(m):       assert 0

def sbc_r(m, reg):  assert 0
def sbc_m(m):       assert 0
def sbc_i(m):       assert 0

def cmp_r(m, reg):  assert 0
def cmp_m(m):       assert 0
def cmp_i(m):       assert 0
