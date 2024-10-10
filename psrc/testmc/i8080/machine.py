from    itertools  import chain

from    testmc.generic  import *
from    testmc.i8080.opcodes  import OPCODES, Instructions as I
from    testmc.i8080.opimpl  import InvalidOpcode, incword, readbyte

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
                      Bit(0), Flag('P'), Bit(1), Flag('C') )
        srname    = 'f'     # Flags Register

    #   This is broken for 8080 becuase we also have conditional RET
    #   instructions. The problem is, when we reach one of those we
    #   don't yet know if the RET will be taken, but call() currently
    #   assumes that it will be taken, checks the stack depth, and
    #   returns if necessary. Possibly call could speculatively execute
    #   the conditional RET to see if it will return, and then DTRT.
    _RTS_opcodes    = set([I.RET])

    _ABORT_opcodes  = set()     # XXX

    def reset(self):    self.pc = 0

    def _getpc(self):   return self.pc
    def _getsp(self):   return self.sp

    #   XXX pull up to superclass?
    InvalidOpcode = InvalidOpcode

    #   XXX pull up to superclass?
    class NotImplementedError(Exception):
        ''' Get rid of this once we're more complete. ''' # XXX

    def _step(self):
        opcode = readbyte(self)
        _, fn = OPCODES.get(opcode, (None, None))
        if not fn:
            raise self.NotImplementedError(
                'opcode=${:02X} pc=${:04X}'
                .format(opcode, incword(self.pc, -1)))
        fn(self)

    def pushretaddr(self, word):
        self.sp -= 2
        self.depword(self.sp+1, word)

    def getretaddr(self):
        return self.word(self.sp+1)

    ####################################################################
    #   Tracing and similar information

    def disasm(self):
        ''' Disassemble, at the PC, an 8080 opcode and its operands using
            Z80 mnemonics.

            This is a pretty quick hack that has not been fully tested.
            It's probably possible to produce nicer output by taking apart
            the mnemonics, e.g., ``LDbc`` → ``ld b,c`` etc.

            TODO: Make this check `self.symtab` for addresses and,
            if present there, print them as symbols?
        '''
        pc = self.regs.pc
        op = self.byte(pc)
        mnemonic, _ = OPCODES[op]
        if mnemonic is None:
            return f'DB {op:02X}'
        if op in self.OPERAND_WORD:
            pc1 = incword(self.regs.pc, 1)
            pc2 = incword(self.regs.pc, 2)
            return f'{mnemonic} {self.mem[pc2] * 0x100 + self.mem[pc1]:04X}'
        if op in self.OPERAND_BYTE:
            return f'{mnemonic} {self.mem[incword(self.regs.pc, 1)]:02X}'
        return mnemonic

    #   Opcodes that take no operand
    OPERAND_WORD = frozenset(chain(
        (0x01, 0x11, 0x21, 0x31),   # ld rr,d16
        (0x09, 0x19, 0x29, 0x39),   # add hl,rr
        (0x03, 0x13, 0x23, 0x33),   # inc rr
        (0x0B, 0x1B, 0x2B, 0x3B),   # dec rr
        (0x0A, 0x1A, 0x02, 0x12),   # lda a,(rr); ld (rr),a
        (0xC3, 0xDA, 0xD2, 0xCA, 0xC2, 0xF2, 0xFA, 0xEA, 0xE2), # jp
        (0xCD, 0xDC, 0xD4, 0xCC, 0xC4, 0xF4, 0xFC, 0xEC, 0xE4), # call
        ))

    OPERAND_BYTE = frozenset(chain(
        (0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E),   # ld r,d8
        (0xC6, 0xCE, 0xD6, 0xDE, 0xE6, 0xEE, 0xF6, 0xFE),   # add r,d8 etc.
        ))
