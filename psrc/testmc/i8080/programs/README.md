Third-party 8080 CPU Test Programs
==================================

All of these have runnable `.COM` binaries supplied;
not all include source (`.ASM` or `.MAC`).

- `8080mac.i80`: An attempt at a heder file that will let [ASL]
  (Macroassembler AS) build `8080PRE.MAC` (below). This does not currently
  work. As a workaround, you can get addresses and data associated with
  instructions by disassembling with `z80dasm` or a similar tool.

- `8080PRE`, `8080EXER`: Ian Bartholomew's [8080/8085 CPU Exerciser][bart]
  (2009-02). These are ports of Frank D. Cringle's `prelim.z80` and
  `zexlax.z80` ([source here][zexlax]) to 8080 and 8085. This consists of
  two programs:
  - `8080PRE` checks that enough functionality works to run the main
    exerciser, and runs quickly (a fraction of a second). It will not catch
    all problems that could keep the main exerciser from running, however.
  - `8080EXER` is mainly test vectors and a framework to run them. It
    is _very_ slow (see below).
  - __NOTE:__ This version of 8080EXER has all CRC values set to 0;
    this needs to be fixed. See below.
  - There is another version of this for the Soviet KR580VM80A CPU (which
    has some undocumented bits), [`8080EX1.MAC`]. That has non-zero
    expected CRCs for the vectors, which makes the all-zero expected CRCs
    for the version above a bit suspcious. Whether those all-zeros are
    correct needs to be investigated.

- `TEST`: [Microcosm Associates 8080/8085 CPU Diagnostic][microcosm]
  (1980). Originally designed to check an Altair 8800. Runs quickly (a
  fraction of a second). Can be built with ASL.

- `CPUTEST`: Diagnostics II, version 1.2, CPU test by Supersoft Associates.
  Source not available, but a GitHub repo has [`CPUTEST.COM`]. Takes 3-4
  minutes to run.

8080EXER
--------

8080EXER is _very_ slow:

> The complete set of tests will take approximately 3 hours 20 minutes to
> run on a 2MHz 8080. However, this figure can be reduced to approximately
> 30 minutes by removing the 8 bit alu tests....

(These tests are the `aluop <b,c,d,e,h,l,m,a>` ones.)

This appears to be even slower on the simulator: in 2e9 cycles (3.5 hours
on a Core i9-9900K, ~7h on an old i5 laptop) it got only this far:

    dad <b,d,h,sp>................ ERROR **** crc expected: 00000000 found: 14474ba6
    aluop nn...................... ERROR **** crc expected: 00000000 found: 52877038
    aluop <b,c,d,e,h,l,m,a>.......

#### CRC Values

The current version here is the "discovery" version that has all-zeros in
the expected CRC fields. Other versions with CRCs from tests on actual
hardware are also available.



<!-------------------------------------------------------------------->
[ASL]: http://john.ccac.rwth-aachen.de:8000/as/
[`8080EX1.MAC`]: https://github.com/begoon/i8080-core/blob/master/asm/8080EX1.MAC
[`CPUTEST.COM`]: https://github.com/JALsnipe/i8080-core/blob/master/CPUTEST.COM
[bart]: https://web.archive.org/web/20141129075303/www.idb.me.uk/sunhillow/8080.html
[microcosm]: https://github.com/begoon/i8080-core/blob/master/asm/TEST.ASM
[zexlax]: https://github.com/agn453/ZEXALL/
