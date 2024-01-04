Third-party 8080 CPU Test Programs
==================================

All of these have runnable `.COM` binaries supplied;
not all include source (`.ASM` or `.MAC`).

- `8080mac.i80`: An attempt at a header file that will let [ASL]
  (Macroassembler AS) build `8080PRE.MAC` (below). This does not currently
  work. As a workaround, you can get addresses and data associated with
  instructions by disassembling with `z80dasm` or a similar tool.

- `TEST`: [Microcosm Associates 8080/8085 CPU Diagnostic][microcosm]
  (1980). Originally designed to check an Altair 8800. Runs quickly (a
  fraction of a second). Can be built with ASL.

- `CPUTEST`: Diagnostics II, version 1.2, CPU test by Supersoft Associates.
  Source not available, but a GitHub repo has [`CPUTEST.COM`]. Takes 3-4
  minutes to run.

- `8080PRE`, `8080EXER`: Ian Bartholomew's [8080/8085 CPU Exerciser][bart]
  (2009-02). These are ports of Frank D. Cringle's `prelim.z80` and
  `zexlax.z80` ([source here][zexlax]) to 8080 and 8085. This consists of
  two programs:
  - `8080PRE` checks that enough functionality works to run the main
    exerciser, and runs quickly (a fraction of a second). It will not catch
    all problems that could keep the main exerciser from running, however.
  - `8080EXER` (not included here) is mainly test vectors and a framework
    to run them. It is _very_ slow (see below). This original version has
    all expected CRC results set to $00000000.
  - `8080EXE1` is the 'INTEL 8080A' version from further down the page
    which has CRC values for the Intel 8080 and many second source
    manufacturers. For more information see "CRC Values" below.


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

The `8080EXER.{MAC,COM}` in the "Basic Exerciser Files" [of the page][bart]
has all the expected CRCs set to `00000000`, so all the tests will fail.
This appears to be the "discovery version" of the exerciser, intended to be
run on an actual CPU to get the correct CRCs against which to test
simulators or whatever.

The version you want to use is one from the "Results" section below that
matches the particular CPU you're trying to emulate. Fortunately, most of
the 8080 CPU implementations (Intel, Nat. Semi., NEC, etc.) all produce the
same CRC values, even the Russian KR580VM80A clone. The "mac" and "com"
links for all of these are to the same files, `8080EX1.MAC` and
`8080EX1.COM`. The latter was apparently built from a slightly different
version of the former, however, as the banner in the source file is "8080
instruction exerciser (Intel and clones)" but the `.COM` file prints "8080
instruction exerciser (KR580VM80A CPU)".

The only exception seems to be the AMD CPUs, which are said there to have a
difference in flags implementation for `ANA` (and maybe `ANI`), perhaps
more like the 8085 than the 8080. (Though my understanding is that it's
different both, always setting the half carry to `0` where the 8085 sets it
to `1`.)



<!-------------------------------------------------------------------->
[ASL]: http://john.ccac.rwth-aachen.de:8000/as/
[`CPUTEST.COM`]: https://github.com/JALsnipe/i8080-core/blob/master/CPUTEST.COM
[bart]: https://web.archive.org/web/20151108135453/http://www.idb.me.uk:80/sunhillow/8080.html
[microcosm]: https://github.com/begoon/i8080-core/blob/master/asm/TEST.ASM
[zexlax]: https://github.com/agn453/ZEXALL/
