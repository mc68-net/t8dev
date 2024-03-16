from    testmc.generic  import *
from    testmc.i8080.opcodes  import OPCODES, Instructions
from    testmc.i8080.opimpl  import (
            InvalidOpcode, incword, readbyte, signedbyteat,
            )

class Machine(GenericMachine):

    def __init__(self, *, memsize=65536):
        super().__init__()
        self.mem = IOMem(memsize)
        self.mem.copyapi(self)

        self.pc = self.a = self.bc = self.de = self.hl = 0
        self.sp = 0xE000
        self.S = self.Z = self.H = self.P = self.C = False

    is_little_endian = True
    def get_memory_seq(self):
        return self.mem

    class Registers(GenericRegisters):
        machname  = 'i8080'
        registers = ( Reg('pc', 16), Reg('a'),
            Reg('bc', 16, split8=1), Reg('de', 16, split8=1),
            Reg('hl', 16, split8=1), Reg('sp', 16) )
           #    Eventually split8 etc. can be implemented like...
           #AliasNarrow('b', 'bc', 8, 0xFF00),
           #AliasNarrow('c', 'bc', 0, 0xFF),
           #AliasCombine('d', ['a','b']),   # 6809 D register
        srbits    = ( Flag('S'), Flag('Z'), Bit(0), Flag('H'),
                      Bit(0), Flag('P'), Bit(0), Flag('C') )
        srname    = 'f'     # Flags Register

    _RTS_opcodes    = set()     # XXX
    _ABORT_opcodes  = set()     # XXX

    def _getpc(self):   return self.pc
    def _getsp(self):   return self.sp

    #   XXX pull up to superclass?
    InvalidOpcode = InvalidOpcode

    #   XXX pull up to superclass?
    class NotImplementedError(Exception):
        ''' Get rid of this once we're more complete. ''' # XXX

    def _step(self):
        opcode = readbyte(self)
        _, f = OPCODES.get(opcode, (None, None))
        if not f:
            raise self.NotImplementedError(
                'opcode=${:02X} pc=${:04X}'
                .format(opcode, incword(self.pc, -1)))
        f(self)

    def pushretaddr(self, word):
        self.sp -= 2
        self.depword(self.sp+1, word)

    def getretaddr(self):
        return self.word(self.sp+1)

