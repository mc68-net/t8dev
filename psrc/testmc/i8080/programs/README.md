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
  `zexlax.z80` to 8080 and 8085. This consists of two programs:
  - `8080PRE` checks that enough functionality works to run the main
    exerciser, and runs quickly (a fraction of a second). It will not catch
    all problems that could keep the main exerciser from running, however.
  - `8080EXER` is mainly test vectors and a framework to run them. In part
    because it does extensive CRC calculations for the test vectors, it
    takes a _very_ long time to run under the simulator.
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



<!-------------------------------------------------------------------->
[ASL]: http://john.ccac.rwth-aachen.de:8000/as/
[`8080EX1.MAC`]: https://github.com/begoon/i8080-core/blob/master/asm/8080EX1.MAC
[`CPUTEST.COM`]: https://github.com/JALsnipe/i8080-core/blob/master/CPUTEST.COM
[bart]: https://web.archive.org/web/20141129075303/www.idb.me.uk/sunhillow/8080.html
[microcosm]: https://github.com/begoon/i8080-core/blob/master/asm/TEST.ASM
