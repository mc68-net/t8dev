from    testmc.generic  import *

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
            Reg('bc', 16), Reg('de', 16), Reg('hl', 16), Reg('sp', 16) )
        srbits    = ( Flag('S'), Flag('Z'), Bit(0), Flag('H'),
                      Bit(0), Flag('P'), Bit(0), Flag('C') )
        srname    = 'f'     # Flags Register

    _RTS_opcodes    = set()     # XXX
    _ABORT_opcodes  = set()     # XXX

    def _getpc(self):   return self.pc
    def _getsp(self):   return self.sp

    def _step(self):
        raise NotImplementedError('XXX Write me!')

    def pushretaddr(self, word):
        self.sp -= 2
        self.depword(self.sp+1, word)

    def getretaddr(self):
        return self.word(self.sp+1)

