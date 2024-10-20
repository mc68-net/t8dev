from    abc  import abstractmethod, abstractproperty
from    collections.abc   import Container
from    itertools  import repeat
from    testmc.generic.memory  import MemoryAccess
from    binary.symtab  import SymTab
from    binary.tool  import asl, asxxxx

class GenericMachine(MemoryAccess): # MemoryAccess is already an ABC
    ''' Superclass for "Machines" that simulate a microprocessor system
        with memory and registers.

        The interface offers the following properties and methods. The ones
        marked with ◑ must be implemented by the subclass; see the
        attribute/method docstrings for details.

        - ◑`MemoryAccess` routines: `byte()`, `word()`, `deposit()`, etc.
          (See that class for subclassing information.)
        - ◑`Registers`: The subclass of `GenericRegisters` that defines
          the registers and flags of the machine.
        - ◑`__init__()`: See method docstring below.
        - `regs`: The current machine registers and flags.
        - `setregs()`: Set some or all machine registers and flags.
    '''

    def biosname(self):
        ''' Many `Machine` subclasses include a simple BIOS used for unit
            testing and by the `testmc.tmc` command-line simulator. This
            is usually the (not qualified) name of the package in which
            that `Machine` subclass resides, which this returns, but this
            can be overridden for `Machine`s that share a BIOS with another
            `Machine`, e.g., ``i8085`` might use the ``i8080`` BIOS.
        '''
        return self.__class__.__module__.split('.')[-2]

    def __init__(self):
        ''' The subclass `__init__()` should call `super().__init__()` and
            initialize memory, registers and flags. The registers and flags
            may be properties on this object itself or on a separate object
            in the `regsobj` property. Create and initialize properties for
            either the individual flags *or* the status register named by
            `Registers.srname`, but not both.
        '''
        self.symtab = SymTab()      # symtab initially empty
        for regspec in self.Registers.registers:
            if regspec.split8:
                self.Registers.init_split8(type(self._regsobj()), regspec)

    @abstractproperty
    def Registers(self):
        ''' The class defining the registers of the machine.

            This is typically a subclass of `GenericRegisters`, and the
            attribute can be defined most easily with a nested class
            declaration in the subclass:

                class Registers(GenericRegisters):
                    registers = (...)
                    srbits = (...)
                    srname = '...'      # optional
        '''

    def _regsobj(self):
        return getattr(self, 'regsobj', self)

    @property
    def regs(self):
        ''' A `Registers` instance containing the current values of the
            machine registers and flags.

            If the `regsobj` attribute has a value, the register values
            will be read from attributes on that object, otherwise they
            will be read from attributes on `self`.

            If `Registers` has an `srname` property *and* `regsobj`/`self`
            has the same property, the `Registers` object will be instiated
            with that property. Otherwise it will be instantiated with the
            indivdiual flags read from the `regsobj`/`self`.
        '''
        R = self.Registers
        srname = R()._srname()
        regsobj = self._regsobj()
        vals = {}
        for reg in R.registers:
            vals[reg.name] = getattr(regsobj, reg.name)
        if srname and hasattr(regsobj, srname):
            vals[srname] = getattr(regsobj, srname)
        else:
            for flag in R.srbits:
                if flag.name:
                    vals[flag.name] = getattr(regsobj, flag.name)
        return R(**vals)

    def setregs(self, r):
        ''' Given a `Registers` object, set the machine's registers and
            flags to the value of any non-`None` values in the `Registers`.

            If `Registers` has a status register name (`srname`) defined,
            that will be set on the target instead of the individual flags.
            This can be overridden by specifying `setsr=False`.
        '''
        setsr = r._srname() and hasattr(self._regsobj(), r._srname())
        r.set_attrs_on(self._regsobj(), setsr=setsr)

    ####################################################################
    #   Object code loading

    def load_memimage(self, memimage, setPC=False):
        ''' Load the given memimage. If `setPC` is `True` and
            `memimage` has an entry point, the machine's program counter
            will be set to that entry point. The entry point (or `None`)
            is always returned.
        '''
        for addr, data in memimage:
            self.deposit(addr, data)
        if memimage.entrypoint is not None:
            self.setregs(self.Registers(pc=memimage.entrypoint))
        return memimage.entrypoint

    def load(self, path, mergestyle='prefcur', setPC=True):
        ''' Load the given file and, if available, symbols. If the file
            has an entry point it will be returned (otherwise `None`
            is returned) and, if `setPC` is `True`, the program counter
            will be set to that entry point.

            The symbol table for the binary, if available, will be merged
            with the machine's existing symbol table using `SymTab.merge()`
            with the given `mergestyle` (default ``prefcur`` to add new
            symbols only if they wouldn't override an existing symbol).

            The symbols file is loaded from the same directory and base
            filename as the input file. The types of files this understands
            are:
            * ``.p`` output from Macroassembler AS and its associated
              ``.map`` file.
            * ``.bin`` CoCo binary format and associated ASxxxx ``.rst``
              linker listing file.
        '''
        path = str(path)                    # We accept path-like objects
        if path.lower().endswith('.p'):
            #   Assume it's Macro Assembler AS output.
            image, symtab = self._load_asl(path)
        else:
            #   Assume it's the basename of ASxxxx toolchain output.
            #   (This should probably be changed to require something
            #   indicating this explicitly.)
            image, symtab = self._load_asxxxx(path)

        entrypoint = self.load_memimage(image, setPC)
        self.symtab.merge(symtab, style=mergestyle)
        return entrypoint

    def _load_asl(self, path):
        image = asl.parse_obj_fromfile(path)
        symtab = None
        mapfile_path = path[0:-2] + '.map'
        try:
            symtab = asl.parse_symtab_fromfile(mapfile_path)
        except FileNotFoundError as err:
            print('WARNING: could not read symbol table file from path ' \
                + mapfile_path, file=stderr)
            print('FileNotFoundError: ' + str(err), file=stderr)
        return image, symtab

    def _load_asxxxx(self, path):
        image = asxxxx.parse_cocobin_fromfile(path + '.bin')
        try:
            symtab = asxxxx.AxSymTab.readsymtabpath(path)
        except FileNotFoundError as err:
            print('WARNING: could not read symbol table file from path ' \
                + path, file=stderr)
            print('FileNotFoundError: ' + str(err), file=stderr)
        return image, symtab

    ####################################################################
    #   Execution - abstract methods

    @abstractproperty
    def _ABORT_opcodes(self):
        ''' The default set of opcodes that should abort the execution of
            `call()`. This must be a `set()` or other object that supports
            the `|` operator for set union.

            Which opcode(s) you choose for this set will depend on both the
            CPU and the conventions of programming on that CPU. For example
            `BRK` is a reasonable abort default on 6502 because it's not
            often used as a call mechanism in 6502 programs, but that is
            not true for the very similar 6800 `SWI` instruction.
        '''

    @abstractmethod
    def reset(self):
        ''' Update the internal set of the simulated CPU as it is when the
            ``RESET`` signal is asserted, up to the point where it would
            start executing instructions.

            This should *not* change any state that the CPU itself does not
            update on reset, i.e., it should leave at the current values
            any registers, memory or other state that the ``RESET`` signal
            does not change. Typically, this just loads the PC with the
            reset vector (reading it from current memory if necessary)
        '''

    @abstractmethod
    def _getpc(self):
        ''' Efficiently return the current program counter value.

            The PC is checked very frequently by `stepto()`, `call()`, etc.
            and checking it via `regs` (which generates a new a Registers
            object each time it's called) slows down stepping by an order
            of magnitude compared to returning the PC value as directly
            as possible from the underlying simulator.
        '''

    @abstractmethod
    def _getsp(self):
        ''' Efficiently return the current stack pointer register value.
            (This should be the register contents, not the address, if they
            differ.) See `_getpc()` for further information.
        '''

    @abstractmethod
    def _step(self):
        ' Execute current opcode (and its arguments), updating machine state. '

    @abstractmethod
    def pushretaddr(self, addr):
        ''' Push return address `addr` on to the stack, such that an RTS
            will return to this address.
        '''

    @abstractmethod
    def getretaddr(self):
        ' Return the address at the top of the stack that RTS would use. '

    ####################################################################
    #   Execution - implementation

    #   Default maximum number of opcodes to execute when using stepto(),
    #   call() and related functions. Even on a relatively slow modern
    #   machine, 100,000 opcodes should terminate within a few seconds.
    MAXSTEPS = 100000

    def step(self, count=1, *, trace=False):
        ''' Execute `count` instructions (default 1).

            If `trace` is `True`, the current machine state and instruction
            about to be executed will be printed before executing the step.

            XXX This should check for stack under/overflow.
        '''
        for _ in repeat(None, count):
            if trace: print(self.traceline())
            self._step()

    def stepto(self, *, stopat=set(), stopon=set(), trace=False,
        maxsteps=MAXSTEPS, raisetimeout=True):
        ''' Step an opcode and then continue until an address in `stopat`
            or an opcode in `stopon` is reached, or until we have done
            `maxsteps`. (At least one opcode is always executed.) Return
            the number of steps executed.

            An attempt to exceed `maxsteps` will raise a `Timeout`
            exception; if you want to run just a specific number of steps
            use `step()` instead. Any other stop condition simply returns.

            `stopat` and `stopon` are checked to ensure that they are
            `collections.abc.Container` instances.
        '''
        assert isinstance(stopat, Container), \
            "'stopat' must be a collections.abc.Container"
        assert isinstance(stopon, Container), \
            "'stopon' must be a collections.abc.Container"

        remaining = maxsteps - 1
        while True:
            self.step(trace=trace)
            pc = self._getpc()
            if pc in stopat or self.byte(pc) in stopon:
                break
            if remaining <= 0:
                if raisetimeout:
                    self._raiseTimeout(maxsteps)
                else:
                    return maxsteps
            remaining -= 1
        return maxsteps - remaining

    def _raiseTimeout(self, n):
        raise self.Timeout(
            'Timeout after {} opcodes: {} opcode={}' \
            .format(n, self.regs, self.byte(self._getpc())))

    CALL_DEFAULT_RETADDR = 0xFFFD

    def call(self, addr, regs=None, *, retaddr=CALL_DEFAULT_RETADDR,
            stopat=None, stopon=None, maxsteps=MAXSTEPS, trace=False):
        ''' Set the given registers, push `retaddr` on the stack, and start
            execution at `addr`. Execution stops when:
            - we are about to execute an address in `stopat`
            - we are about to execute at `retaddr` and the stack has
              nothing on it (i.e., it points to the same location as when
              this function was called)
            - `maxsteps` instructions have been executed, raising `Timeout`
            - we are about to execute an opcode in `stopon`, raising `Abort`

            On successful exit:
            - The program counter will be left at `retaddr`.
            - The stack pointer will be left at the location it was when
              this function was called.

            Default parameter values are:
            - Stack pointer: the the `Machine.Registers`'s default initial
              stack pointer value, which should have been set to something
              usable at initialization.
            - `retaddr`: `CALL_DEFAULT_RETADDR`, an address (hopefully)
              unlikely to be used by the program under test,
            - `stopon`: the set of instructions in `_ABORT_opcodes`.
            - `trace`: False; `step()` tracing will be enabled if True.

            `addr` may be set to `None` to use the program counter in
            `regs`, but will aways override the `regs` PC otherwise.
        '''
        if regs is None: regs = self.Registers()
        self.setregs(regs)

        if addr is not None:
            #   `addr` always overrides the PC in `regs`, but `addr`
            #   may be explicitly set to `None` to use it.
            self.setregs(self.Registers(pc=addr))

        if stopat is None:  stopat = set()
        else:               stopat = set(stopat)
        stopat.add(retaddr)

        if stopon is None:                      stopon = self._ABORT_opcodes
        if not isinstance(stopon, Container):   stopon = (stopon,)
        stopon = set(stopon)                    # should be faster lookup

        allstopon = set(stopon)
        maxremain = maxsteps
        initsp = self._getsp()
        self.pushretaddr(retaddr)
        while True:
            pc = self._getpc()
            if pc in stopat:  return
            if pc == retaddr and self._getsp() == initsp:
                #   We're about to execute at the return address we pushed
                #   on the stack, and the stack is empty, so this means
                #   that the program under test returned.
                return
            if maxremain <= 0:
                self._raiseTimeout(maxsteps)
            opcode = self.byte(pc)
            if opcode in stopon:
                raise self.Abort('Abort on opcode=${:02X}: {}' \
                    .format(self.byte(pc), self.regs))
            maxremain -= self.stepto(stopat=stopat, stopon=allstopon,
                maxsteps=maxremain, raisetimeout=False, trace=trace)

    ####################################################################
    #   Tracing and similar information

    class Timeout(RuntimeError):
        ' The emulator ran longer than requested. '

    class Abort(RuntimeError):
        ' The emulator encoutered an instruction on which to abort.'

    def traceline(self):
        ''' Return a line of tracing information about the current step of
            the execution. This just prints the current registers and
            opcode; it could be extended to print stack or other
            information as well.
        '''
        #   Ideally this could do some proper disassembly and print a bit
        #   of the stack as well. Printing the stack might also want somehow
        #   to indicate where the stack started at the beginning of the test.
        return '{} {}'.format(self.regs, self.disasm())

    def disasm(self):
        ''' Return a human-readable representation of the current instruction
            at the PC. The default implementation just prints the hex opcode;
            typically this will be overridden with a function that returns
            a nicer disassembly.
        '''
        return 'opcode={:02X}'.format(self.byte(self.regs.pc))

    ####################################################################
    #   Utilities for use by test modules

    @classmethod
    def rs(cls, objfile):
        ''' Return a pair ``(R,S)`` of the `Registers` for this machine and
            the `symtab` that results from loading `objfile`.
        '''
        m = cls()
        m.load(objfile)
        return m.Registers, m.symtab
