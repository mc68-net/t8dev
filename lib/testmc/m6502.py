''' testmc.m6502 - test framework for 6502 microcomputer code

    This uses the py65 emulator to emulate a 6502 microcomputer system.
'''

from    collections  import namedtuple
from    collections.abc   import Container, Sequence
from    itertools  import repeat
from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    sys import stderr

from    testmc.asxxxx import MemImage, SymTab

__all__ = ['Registers', 'Machine']

RegistersTuple = namedtuple('RegistersTuple', 'pc a x y sp N V D I Z C')
class Registers(RegistersTuple):
    ''' The register set, including flags, of the 6502.

        Any values set to `None` will be ignored in comparisons
        between two register sets.

        Register names are lower-case; flags are upper-case. The
        registers in the constructor are given in order of
        approximately how likely you are to want to check them for
        comparisons. The flags given in the program status register
        order (MSB first); you will almost invariably want to set
        those by name, or by instead passing in a program status
        register value `psr`.

        repr() returns the processor name, register values in
        hexadecimal and a flags list with the flag letter upper-case
        if set, lower-case if clear. Any values that are `None`
        (ignored in comparisons) will be printed with hyphens. repr()
        is overridden instead of just str() because pytest prints
        repr() output, and that's where we want easily to see what's
        wrong.

        This inherits from `tuple` for immutability.
    '''

    def __new__(cls,
            pc=None, a=None, x=None, y=None, sp=None,
            N=None, V=None, D=None, I=None, Z=None, C=None,
            psr=None):

        def checkvalue(n):
            try:
                if n is None or n >= 0: return
            except TypeError:
                pass
            raise ValueError('bad value: {}'.format(n))
        [ checkvalue(n) for n in [pc, a, x, y, sp, N, V, D, I, Z, C, psr] ]

        if psr is not None:
            if psr < 0 or psr > 0xff:
                raise AttributeError('invalid psr: ' + hex(psr))
            if [f for f in [Z, C, N, V, I, D] if f is not None]:
                raise AttributeError("must not give both psr and flag values")
            C = 1 if psr & 0x01 else 0
            Z = 1 if psr & 0x02 else 0
            I = 1 if psr & 0x04 else 0
            D = 1 if psr & 0x08 else 0
            V = 1 if psr & 0x40 else 0
            N = 1 if psr & 0x80 else 0

        self = super(Registers, cls) \
            .__new__(cls, pc, a, x, y, sp, N, V, D, I, Z, C)
        return self

    def __repr__(self):
        pc = '----' if self.pc is None else '{:04X}'.format(self.pc)
        a  =   '--' if self.a  is None else '{:02X}'.format(self.a )
        x  =   '--' if self.x  is None else '{:02X}'.format(self.x )
        y  =   '--' if self.y  is None else '{:02X}'.format(self.y )
        sp =   '--' if self.sp is None else '{:02X}'.format(self.sp)
        def f(char, val):   # flag letter and value
            if val is None: return '-'
            if val is 0:    return char.lower()
            if val is 1:    return char.upper()
            return '?'
        return '6502 pc={} a={} x={} y={} sp={} {}{}--{}{}{}{}' \
            .format(pc, a, x, y, sp,
                f('N', self.N), f('V', self.V),
                f('D', self.D), f('I', self.I), f('Z', self.Z), f('C', self.C))

    def __ne__(a, b):
        #   Not sure if I'm seeing problems w/the default version
        #   delegating to __eq__, but this should definitely fix it.
        return not a.__eq__(b)

    def __eq__(a, b):
        if type(a) != type(b): return False

        #print('a:', a, '\nb:', b)
        def comp(a, b): # Should we compare a and b?
            #print('comp({}, {}) → {})'.format(a, b, a is not None and b is not None))
            return a is not None and b is not None

        if comp(a.pc, b.pc) and a.pc != b.pc: return False
        if comp(a.a , b.a ) and a.a  != b.a : return False
        if comp(a.x , b.x ) and a.x  != b.x : return False
        if comp(a.y , b.y ) and a.y  != b.y : return False
        if comp(a.sp, b.sp) and a.sp != b.sp: return False
        if comp(a.V , b.V ) and a.V  != b.V : return False
        if comp(a.D , b.D ) and a.D  != b.D : return False
        if comp(a.I , b.I ) and a.I  != b.I : return False
        if comp(a.Z , b.Z ) and a.Z  != b.Z : return False
        if comp(a.C , b.C ) and a.C  != b.C : return False

        return True

class Machine():

    class Timeout(RuntimeError):
        ' The emulator ran longer than requested. '
        pass

    class Abort(RuntimeError):
        ' The emulator encoutered an instruction on which to abort.'
        pass

    def __init__(self):
        self.mpu = MPU()
        self.symtab = SymTab([], [])

    @property
    def regs(self):
        m = self.mpu
        return Registers(m.pc, m.a, m.x, m.y, m.sp, psr=m.p)

    def setregs(self, pc=None, a=None, x=None, y=None, sp=None):
        m = self.mpu
        if pc is not None:  m.pc = pc
        if  a is not None:   m.a =  a
        if  x is not None:   m.x =  x
        if  y is not None:   m.y =  y
        if sp is not None:  m.sp = sp
        #   We don't do processor status register here as flags should
        #   be set/reset individually, particularly because we should
        #   avoid ever changing unused bits 5 and 6.

    def setregisters(self, r):
        for flag in (r.N, r.V, r.D, r.I, r.Z, r.C):
            if flag is not None:
                raise ValueError("Cannot yet supply flags to setregisters()")
        return self.setregs(r.pc, r.a, r.x, r.y, r.sp)

    #   XXX This "examine" interface isn't so nice. Perhaps we can condense
    #   in down to a single examine() function that takes a length and type?

    def byte(self, addr):
        ' Examine a byte from memory. '
        return self.mpu.ByteAt(addr)

    def bytes(self, addr, len):
        ' Examine a list of bytes from memory. '
        vals = []
        for i in range(addr, addr+len):
            vals.append(self.byte(i))
        return vals

    def word(self, addr):
        ''' Examine a word from memory.
            Native endianness is decoded to give a 16-bit int.
        '''
        return self.mpu.WordAt(addr)

    def words(self, addr, len):
        ' Examine a list of words from memory. '
        vals = []
        for i in range(addr, addr+len*2, 2):
            vals.append(self.word(i))
        return vals

    def _stackaddr(self, depth, size):
        addr = 0x100 + self.mpu.sp + 1 + depth
        if addr >= 0x201 - size:
            raise IndexError("stack underflow: addr={:04X} size={}" \
                .format(addr, size))
        return addr

    def spbyte(self, depth=0):
        return self.byte(self._stackaddr(depth, 1))

    def spword(self, depth=0):
        return self.word(self._stackaddr(depth, 2))

    def str(self, addr, len):
        ' Examine a string from memory. '
        #   This currently throws an exception if any of the bytes
        #   in the memory range are >0x7f. It's not clear how we
        #   should be decoding those. Possibly we want an option to
        #   clear the high bit on all chars before decoding.
        return bytes(self.mpu.memory[addr:addr+len]).decode('ASCII')

    def deposit(self, addr, value):
        ''' Deposit `value` to memory at `addr`. `value` must be a
            `numbers.Integral` between 0x00 and 0xFF, or a `Sequence`
            of such numbers in which case the elements will be
            deposited at contiguous addresses starting at `addr`.
        '''
        if isinstance(value, Sequence):
            for i, v in enumerate(value):
                self.deposit(addr+i, v)
        else:
            if addr < 0x0000 or addr > 0xFFFF:
                raise ValueError('Bad address ${:04X}' \
                    ' to deposit byte value ${:02X}'.format(addr, value))
            if not isinstance(value, Integral):
                raise ValueError('Bad (non-integral) byte value {} ' \
                    'to deposit at addr ${:04X}'.format(value, addr))
            if value < 0x00 or value > 0xFF:
                raise ValueError('Bad byte value ${:02X}'
                    ' to deposit at addr ${:04X}'.format(value, addr))
            self.mpu.memory[addr] = value

    def depwords(self, addr, values):
        ''' Deposit each int from the list as a 16-bit word, starting
            at `addr`. The values are converted to native endianness.
        '''
        bytes = []
        for i in values:
            bytes.append(i  % 256)
            bytes.append(i // 256)
        self.deposit(addr, bytes)

    def load(self, path):
        ''' Load the given ``.bin`` file and, if available, the
            symbols from a ``.rst`` (ASxxxx linker listing file)
            in the same directory.
        '''
        self.load_memimage(MemImage.parse_cocobin_fromfile(path + '.bin'))
        try:
            self.symtab = SymTab.readsymtabpath(path)
        except FileNotFoundError as err:
            print('WARNING: could not read symbol table file from path ' \
                + path, file=stderr)
            print('FileNotFoundError: ' + str(err), file=stderr)

    def load_memimage(self, memimage):
        for addr, data in memimage:
            self.deposit(addr, data)
        self.mpu.pc = memimage.entrypoint

    def step(self, count=1, *, trace=False):
        ''' Execute `count` instructions (default 1).

            If `trace` is `True`, the current machine state and
            instruction about to be executed will be printed
            before executing the step.

            XXX This should check for stack under/overflow.
        '''
        for _ in repeat(None, count):
            if trace:
                print('{} opcode={:02X}' \
                    .format(self.regs, self.byte(self.regs.pc)))
            self.mpu.step()

    #   Default maximum number of instructions to execute when using
    #   stepto(), call() and related functions. Even on a relatively
    #   slow modern machine, 100,000 instructions should terminate
    #   within a few seconds.
    MAXOPS = 100000

    def stepto(self, instrs, *, maxops=MAXOPS, trace=False):
        ''' Step an instruction and then continue stepping until an
            instruction in `instrs` is reached. Raise a `Timeout`
            after `maxops`.
        '''
        if not isinstance(instrs, Container):
            instrs = (instrs,)
        self.step(trace=trace)
        count = maxops - 1
        while self.byte(self.mpu.pc) not in instrs:
            self.step(trace=trace)
            count -= 1
            if count <= 0:
                raise self.Timeout(
                    'Timeout after {} instructions: {} opcode={}' \
                    .format(maxops, self.regs, self.byte(self.regs.pc)))

    def call(self, addr, regs=Registers(), *,
            maxops=MAXOPS, aborts=(0x00,), trace=False):
        ''' Simulate a JSR to `addr`, after setting any `registers`
            specified, returning when its corresponding RTS is
            reached.

            A `Timeout` will be raised if `maxops` instructions are
            executed. An `Abort` will be raised if any instructions in
            the `aborts` collection are about to be executed. (By
            default this list contains ``BRK``.) `step()` tracing will
            be enabled if `trace` is `True`.

            The PC will be left at the final (unexecuted) RTS
            instruction. Thus, unlike `step()`, this may execute no
            instructions if the PC is initially pointing to an RTS.

            JSR and RTS instructions will be tracked to allow the
            routine to call subroutines, but tricks with the stack
            (such as pushing an address and executing RTS, with no
            corresponding JSR) will confuse this routine and may
            cause it to terminate early or not at all.
        '''
        self.setregisters(regs)
        if addr is not None:
            self.setregs(pc=addr)       # Overrides regs
        I = Instructions
        stopon = (I.JSR, I.RTS) + tuple(aborts)
        depth = 0
        while True:
            opcode = self.byte(self.mpu.pc)
            if opcode == I.RTS:
                if depth > 0:
                    depth -=1
                else:
                    #   We don't execute the RTS because no JSR was called
                    #   to come in, so we may have nothing on the stack.
                    return
            elif opcode == I.JSR:
                #   Enter the new level with the next execution
                depth += 1
            elif opcode in stopon:   # Abort
                raise self.Abort('Abort on opcode={}: {}' \
                    .format(self.byte(self.regs.pc), self.regs))
            self.stepto(stopon, maxops=maxops, trace=trace)

class Instructions():
    ''' Opcode constants for the 6502, named after the assembly
        instructions.

        There are often multiple opcodes per instruction, one for each
        of the different addressing modes. We distinguish these with a
        lower-case suffix:

                             implied
                  #nn        immediate
            z     nn         zero page
            zx    nn,X       zero indexed by X
            zy    nn,Y       zero indexed by Y
            a     addr       absolute (extended)
            ax    addr,X     absolute,X
            ay    addr,Y     absolute,Y
            i     [addr]     indirect
            ix    [addr,X]   indexed indirect
            iy    [addr],Y   indirect indexed


        One day we might find it worthwhile to have an Assembler class
        that can itself determine correct addressing modes and whatnot
        when assembling instructions, but there doesn't seem to be any
        gain from that at the moment.
    '''

    BRK     = 0x00
    JSR     = 0x20
    RTS     = 0x60
    LDXz    = 0xA6
    LDA     = 0xA9
    INY     = 0xC8
    INX     = 0xE8
    NOP     = 0xEA
