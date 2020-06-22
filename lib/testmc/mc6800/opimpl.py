''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing to its opcode. The function is responsible
    for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

####################################################################
#   Tests of values for setting flags (HINZVC)

def isnegative(b):
    return 0 != b & 0b10000000

def iszero(b):
    return b == 0

def incword(word, addend):
    ''' Return 16-bit `word` incremented by `addend` (which may be negative).
        This returns a 16-bit unsigned result, wrapping at $FFFF/$0000.
    '''
    return (word + addend) & 0xFFFF

def popword(m):
    m.sp = incword(m.sp, 1)
    msb = m.byte(m.sp)
    m.sp = incword(m.sp, 1)
    lsb = m.byte(m.sp)
    return (msb << 8) + lsb

####################################################################
#   Opcode implementations

def nop(m):
    m.pc = incword(m.pc, 1)

def rts(m):
    m.pc = popword(m)

def ldaa(m):
    m.a = m.byte(m.pc+1)
    m.N = isnegative(m.a)
    m.Z = iszero(m.a)
    m.V = False
    m.pc = incword(m.pc, 2)