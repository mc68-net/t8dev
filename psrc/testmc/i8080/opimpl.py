''' Implementation of opcodes.
'''

#   XXX This contains a _lot_ of code copied from testmc.mc6800.opimpl;
#   the common code should be pulled up to testmc.generic.opimpl.

from    warnings  import warn

####################################################################

class InvalidOpcode(RuntimeError):
    ''' Since it is designed for testing code, the simulator
        will not execute invalid opcodes, instead raising an exception.
    '''
    def __init__(self, opcode, regs):
        self.opcode = opcode; self.regs = regs
        super().__init__('op=${:02X}, {}'.format(opcode, regs))

def invalid(m):
    #   The PC has already been advanced past the opcode; undo this.
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
#   Jumps

def jp(m, take=True):
    ''' Read an absolute jump instruction and its operand, but do not
        actually take the jump unless `take` is `True`.
    '''
    target = readword(m)
    if take: m.pc = target

def jp_f(m, flag):      jp(m,     getattr(m, flag))
def jp_nf(m, flag):     jp(m, not getattr(m, flag))

def jp_hl(m):           m.pc = m.hl

def rst(m, addr):       m.pc = addr

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

def pushaf(m):          pushbyte(m, m.a); pushbyte(m, m.regs.f)
def popaf(m):           m.setregs(m.Registers(f=popbyte(m))); m.a = popbyte(m)
def push(m, regs):      pushword(m, getattr(m, regs))
def pop(m, regs):       setattr(m, regs, popword(m))

def call(m, take=True):
    ''' Read an absolute call instruction and its operand, but do not
        actually execute the call unless `take` is `True`.
    '''
    target = readword(m)
    if take:
        pushword(m, m.pc)
        m.pc = target

def  call_f(m, flag):   call(m,     getattr(m, flag))
def call_nf(m, flag):   call(m, not getattr(m, flag)) 

def ret(m, take=True):
    if not take: return
    m.pc = popword(m)

def ret_f(m, flag):     ret(m,     getattr(m, flag))
def ret_nf(m, flag):    ret(m, not getattr(m, flag)) 

def ex_sthl(m):         tmp = m.word(m.sp); m.depword(m.sp, m.hl); m.hl = tmp

####################################################################
#   Register Moves (Load/Store)

def ld_rr(m, dst, src): setattr(m, dst, getattr(m, src))
def ld_ri(m, dst):      setattr(m, dst, readbyte(m))
def ld_mr(m, src):      m.mem[m.hl] = getattr(m, src)
def ld_mi(m):           m.deposit(m.hl, readbyte(m))
def ld_rm(m, dst):      setattr(m, dst, m.mem[m.hl])
def ld_ax(m):           m.a = m.mem[readword(m)]
def ld_xa(m):           m.mem[readword(m)] = m.a

def ld_aqbc(m):         m.a = m.byte(m.bc)
def ld_aqde(m):         m.a = m.byte(m.de)
def ld_qbca(m):         m.deposit(m.bc, m.a)
def ld_qdea(m):         m.deposit(m.de, m.a)

def ld_hlx(m):          m.hl = m.word(readword(m))
def ld_xhl(m):          m.depword(readword(m), m.hl)

#   XXX these names need to be Z80'd, I think.
def lxib(m):            m.bc = readword(m)
def lxid(m):            m.de = readword(m)
def lxih(m):            m.hl = readword(m)
def lxis(m):            m.sp = readword(m)

def ld_sphl(m):         m.sp = m.hl
def ex_dehl(m):         tmp = m.de; m.de = m.hl; m.hl = tmp

####################################################################
#   Logic Instructions

def iszero(b):      return b == 0

def isneg(b):       sign = b & (1 << 7); return 0 !=  sign

def parity(byte):
    #   _Hacker's Delight,_ 2nd ed, §5.2, p.100
    p = byte ^ (byte>>1)
    p = p ^ (p>>2)
    p = p ^ (p>>4)
    return not (p&1)

def logicF(m, val, H=False):
    ''' Flag updates for logic operations (mainly):
        • Update sign, zero and parity flags based on `val`.
        • Always clear carry.
        • Clear half carry unless `H` is supplied and is `True`.
    '''
    m.S = isneg(val)
    m.Z = iszero(val)
    m.P = parity(val)
    m.H = H
    m.C = False
    return val

def scf(m):         m.C = True
def ccf(m):         m.C = not m.C

def cpl(m):         m.a = m.a ^ 0xFF

def and_orig(m, a, b):
    ' Original 8080 ACA (and ANI???) half-carry handling. '
    return logicF(m, a & b, H=((a|b)&0x8) != 0)

def and_new(m, a, b):
    ' 8085 and Z80 half-carry handling '
    return logicF(m, a & b, H=1)

def and_r(m, reg):  m.a = and_orig(m, m.a, getattr(m, reg))
def and_m(m):       m.a = and_orig(m, m.a, m.mem[m.hl])
def and_i(m):       m.a = and_orig(m, m.a, readbyte(m)) # XXX and_new on 8080?

def  or_r(m, reg):  m.a = logicF(m, m.a | getattr(m, reg))
def  or_m(m):       m.a = logicF(m, m.a | m.mem[m.hl])
def  or_i(m):       m.a = logicF(m, m.a | readbyte(m))

def xor_r(m, reg):  m.a = logicF(m, m.a ^ getattr(m, reg))
def xor_m(m):       m.a = logicF(m, m.a ^ m.mem[m.hl])
def xor_i(m):       m.a = logicF(m, m.a ^ readbyte(m))

def rlca(m):
    rbit = (m.a & 0x80) != 0
    m.a = ((m.a << 1) & 0xFF) | rbit
    m.C = rbit

def rla(m):
    rbit = (m.a & 0x80) != 0
    m.a = ((m.a << 1) & 0xFF) | m.C
    m.C = rbit

def rrca(m):
    rbit = (m.a & 0x01) != 0
    m.a = (m.a >> 1) | (0x80 if rbit else 0)
    m.C = bool(rbit)

def rra(m):
    rbit = (m.a & 0x01) != 0
    m.a = (m.a >> 1) | (0x80 if m.C else 0)
    m.C = bool(rbit)

####################################################################
#   Increment/Decrement

def inc_r(m, reg):
    val = incbyte(getattr(m, reg), 1)
    setattr(m, reg, logicF(m, val, H=(val & 0xF) == 0x0))

def inc_m(m):
    val = incbyte(m.mem[m.hl], 1)
    m.mem[m.hl] = logicF(m, val, H=(val & 0xF) == 0x0)

#   XXX For DCR, half-carry flag is not-half-borrow! This has been tested
#   by cjs only on an 8085, but that always sets the half-carry flag on a
#   decrement unless the low nybble rols over from a 0 to an F.

def dec_r(m, reg):
    val = incbyte(getattr(m, reg), -1)
    setattr(m, reg, logicF(m, val, H=(val & 0xF) != 0xF))

def dec_m(m):
    val = incbyte(m.mem[m.hl], -1)
    m.mem[m.hl] = logicF(m, val, H=(val & 0xF) != 0xF)

def inx_r(m, reg):
    setattr(m, reg, incword(getattr(m, reg),  1))

def dcx_r(m, reg):
    setattr(m, reg, incword(getattr(m, reg),  -1))

####################################################################
#   Arithmetic

def add(m, augend, addend, carry=0):
    ''' Return the modular 8-bit sum of adding `augend` (the accumulator),
        `addend` (the operand) and `carry`, setting flags appropriately.
    '''
    sum = incbyte(augend, addend)
    sum = incbyte(sum, carry)
    logicF(m, sum)    # set logic flags

    #   Stolen from the MC6800 code (which is from PRG pages A-4 and A-5).
    bit7 = 0b10000000;              bit3 = 0b1000
    x7 = bool(augend & bit7);       x3 = bool(augend & bit3)
    m7 = bool(addend & bit7);       m3 = bool(addend & bit3)
    r7 = bool(sum & bit7);          r3 = bool(sum & bit3)
   #print(f'XXX add   C={m.C} H={m.H} x7={x7} m7={m7} r7={r7}')
    m.C = x7 and m7  or  m7 and not r7  or  not r7 and x7
    m.H = x3 and m3  or  m3 and not r3  or  not r3 and x3
   #print(f'XXX add → C={m.C} H={m.H} sum=${sum:02X}')
    #   Overflow available only on Z80.
    #m.V = x7 and m7 and not r7  or  not x7 and not m7 and r7

    return sum

def broken_sub(m, minuend, subtrahend, borrow=0):
    #   This doesn't work: the carry/borrow calculation appears to be borked.
    addend = ((subtrahend ^ 0xFF) + 1) & 0xFF
   #print(f'\nsub {minuend:02X} {subtrahend:02X}→{addend:02X} B={borrow}')
    val = add(m, minuend, addend, borrow)
   #print(f'  = {val:02X} B={m.C}')
    return val

def sub(m, minuend, subtrahend, borrow=0):
    difference = incbyte(minuend, -subtrahend)
    difference = incbyte(difference, -borrow)
    logicF(m, difference)

    bit7 = 0b10000000;              bit3 = 0b1000
    x7 = bool(minuend & bit7);      x3 = bool(minuend & bit3)
    m7 = bool(subtrahend & bit7);   m3 = bool(subtrahend & bit3)
    r7 = bool(difference & bit7);   r3 = bool(difference & bit3)
    #   The following is copied pretty much directly from the PRG,
    #   page A-31 (CMP).
   #print(f'XXX sub   C={m.C} H={m.H} x7={x7} m7={m7} r7={r7}')
    m.C = (not x7 and m7) or (m7 and r7) or (r7 and not x7)
    m.H = ((subtrahend & 0x0F) + borrow) > (minuend & 0x0F)
   #print(f'XXX sub → C={m.C} H={m.H} diff=${difference:02X}')
    #   Overflow on Z80 only.
    #m.V = (x7 and not m7 and not r7) or (not x7 and m7 and r7)

    return difference

def add_r(m, reg):  m.a = add(m, m.a, getattr(m, reg))
def add_m(m):       m.a = add(m, m.a, m.mem[m.hl])
def add_i(m):       m.a = add(m, m.a, readbyte(m))

def adc_r(m, reg):  m.a = add(m, m.a, getattr(m, reg),  m.C)
def adc_m(m):       m.a = add(m, m.a, m.mem[m.hl],      m.C)
def adc_i(m):       m.a = add(m, m.a, readbyte(m),      m.C)

def sub_r(m, reg):  m.a = sub(m, m.a, getattr(m, reg))
def sub_m(m):       m.a = sub(m, m.a, m.mem[m.hl])
def sub_i(m):       m.a = sub(m, m.a, readbyte(m))

def sbc_r(m, reg):  m.a = sub(m, m.a, getattr(m, reg),  m.C)
def sbc_m(m):       m.a = sub(m, m.a, m.mem[m.hl],      m.C)
def sbc_i(m):       m.a = sub(m, m.a, readbyte(m),      m.C)

def cmp_r(m, reg):        sub(m, m.a, getattr(m, reg))
def cmp_m(m):             sub(m, m.a, m.mem[m.hl])
def cmp_i(m):             sub(m, m.a, readbyte(m))

def add_hlrr(m, reg):
    sum = m.hl + getattr(m, reg)
    #   8080 affects only carry flag
    #   XXX Z80 affects carry and half-carry, and also resets N!
    if sum > 0xFFFF:    m.C = True
    else:               m.C = False
    m.hl = sum & 0xFFFF

def daa(m):
   #print(f'XXX daa   a=${m.a:02X} C={int(m.C)} H={int(m.H)}')
    val = m.a
    lsn = val & 0x0F
    if m.H or (lsn > 9):   val += 0x06; m.H = True
    msn = (val >> 4) & 0x0F
    if m.C or (msn > 9):   val += 0x60; m.C = True
    val = val & 0xFF
    m.a = val & 0xFF
   #print(f'XXX daa → a=${m.a:02X} C={int(m.C)} H={int(m.H)}')

####################################################################
#   Misc.

def nop(m):         return

def di(m):
    ''' Disabling interrupts is a no-op as we don't (currently)
        generate interrupts in the simulator.
    '''
    pass

def ei(m):
    ''' Enabling interrupts is a no-op as we don't (currently)
        generate interrupts in the simulator.

        However, we do emit a warning on encountering this, as if someone
        is testing code with an ``EI`` in it, they may have made an error
        somewhere.

        The warning will by default appear only once when this routine
        is called outside of pytest; for dealing with this in pytest
        see the pytest docs_.

        docs_: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    '''
    warn(f'EI (${m.byte(m.pc-1):02X}) at ${m.pc:04X},'
        ' but simulator will not generate interrupts')
