t8dev: Tools for 8-bit cross-development
========================================

__WARNING:__ This documentation is not currently up to date. Currently
it's best to [contact cjs](#contact-infomation) and get him to help
you set up the t8dev submodule for your development project.

#### Contents

- Introduction
- File and Directory Organization
  - ASL (The Macroassembler AS) Notes
  - ASxxxx Notes
- Third-party Development Tools
  - VICE: The Versatile Commodore Emulator
  - MAME Multi-system Emulators
- Additional Third-party Tools
  - VICE: The Versatile Commodore Emulator
  - MAME Multi-system Emulators
- Additional Tool Information
  - Playing CMT (Cassette Tape) Images
  - The py65 Monitor


Introduction
------------

The `t8dev` package (and it's associated `r8format` package) supports
development of programs in 8-bit assembly languages (for a variety of
platforms) and tools to aid this development. The `t8dev` build tool does
most of the heavy lifting, but there are various other tools included as
well.

See [`doc/setup.md`] for details on setting up a project to use t8dev.

Unit tests are written in [pytest] and use Python-based CPU simulators to
run the assembled code and check the results. (These include `testmc.i8080`
for Intel 8080,  `testmc.mc6800` for Motorola 6800, and [py65] for
MOS 6502.)

The `t8dev.toolset` packages build and install various development tools
such as [Macroassembler AS][asl], other assemblers, binary file and disk
image tools, and 8-bit microcomputer emulators.

This currently has been tested only under Linux (mainly Debian), but should
work under MacOS and other Unices. It likely can be made to work under
Windows as well, if there's demand; [contact cjs](#contact-infomation) if
you're interested in getting support for this.


File and Directory Organization
-------------------------------

Here is an overview of the major files and directories in this repo.

Files:
- [`README.md`]: This file.
- [`Test`]: Installs third-party tools where necessary, builds the code and
  runs the unit tests. (Bash.)
- [`pactivate`]: When sourced in Bash (`. ./pactivate`) activates the
  Python virtual environment, building a new one (and installing the packages
  listed in [`requirements.txt`], such as py65 and pytest) if necessary. You
  can also directly run programs in the virtual environment without
  separately activating it by running them from `.build/virtualenv/bin/`.
  Deactivate the virtual environment with `deactivate`.

Directories:
- [`bin/`]: Development tools/scripts.
- [`tool/`]: Third-party tool installation.
- [`lib/testmc/`]: Unit test library Python module.
- [`src/`]: Assembly source code, unit tests and documentation. These are
  generally modules used by full programs under `exe/`.
- [`exe/`]: "Top-level" assembly files for full executable program builds,
  usually just doing configuration and including code from `src/`. See
  [`exe/README`](exe/README.md).
- [`tmp/`]: Ignored; used to keep developer's random files out of the way.


Third-party Development Tools
-----------------------------

Most of the development tools used for code in this repo are downloaded and
built by the scripts under the `tool/` directory. Tools already available
in the path will be used instead; see the `check_installed()` functions in
the setup scripts for details.

__Assemblers__:
- [The Macroassembler AS][asl] is the primary assembler, and supports a
  wide variety of CPUs and microcontrollers.
- The [ASxxxx Cross Assemblers][asxxxx] are optionally available (see
  below), though little used.

__Development Tools__:
- [retroabandon/osimg] supplies ROM BIOS images for emulators and DOS disk
  images used as a base for building test images.
- Vince Weaver's [dos33fsprogs] provides tools for handling Apple II DOS
  3.3 disk images and files.

__Simulators and Emulators__:
- The [py65] 6502 microprocessor simulator ([source][py65-src]) is used to
  run unit tests.
- The [LinApple] Apple II emulator can be used to run Apple II programs.

#### ASL (The Macroassembler AS) Notes

Versions 1.42 builds 205 through at least 218 are broken for t8dev due to
the "Symbols in Segment NOTHING" section disappearing from the map file.
See [`t8dev.toolset.asl`](src/t8dev/toolset/asl.py) for more
details.

#### ASxxxx Notes

The Linux binaries provided for ASxxxx are 32-bit, and on 64-bit systems
will error out with "No such file or directory" when run unless the 32-bit
dynamic linker (`ld-linux.so.2`) and libraries are installed.

For this reason, by default ASxxxx is not installed and used. Use `./Test
-A` to enable assembly and testing of code using ASxxxx. This is a
persistent flag (even across fully clean `./Test -C` builds); remove
`.all-tools` from the top level repository directory to disable it.

To install the 32-bit libraries on a 64-bit Debian 9 system:

    dpkg --add-architecture i386
    apt update
    apt install libc6-i386


Additional Third-party Tools
----------------------------

The following tools do not currently have any specific support in this
repo, but can be useful for testing.

### VICE: The Versatile Commodore Emulator

[VICE] is a suite of simulators for various CBM computers, including PET
models, the VIC-20 and the Commodore 64.

### MAME Multi-system Emulators

You can install or build the latest version from `mamedev.org` or just use
your system packages; on Debian 9 they'd be installed with:

    sudo apt-get install mame mame-tools mame-doc

The documentation installed by `mame-doc`, under
<file:///usr/share/doc/mame-doc/singlehtml/index.html>, is just an older
version of what's found at <https://docs.mamedev.org>


Additional Tool Information
---------------------------

### Playing CMT (Cassette Tape) Images

`bin/cmtconv` is used to generate `.wav` files that can be played
into microcomputers. It can be handy to play these directly from your
development host, and even more handy to add an separate audio interface
(usually USB) to dedicate to this. On Linux systems, `pactl list short
sinks` will show a list of all sink (output) numbers, names and other
information. A name from this list can be passed to `paplay -d NAME
.build/obj/exe/…/….wav` to load the image on your microcomputer.

Recording should be done not with `parec` (which always writes the output
in raw format) but `parecord` (use SIGINT to stop recording):

    parecord --file-format=wav --format=u8 --channels=1 -d SRCNAME FILE.wav

The `pavucontrol` window can be used to view levels during recording and
playback.

### The py65 Monitor

py65 includes a monitor, `py65mon`, that can be run from the command
line. With no options it drops directly into the monitor on a
simulated 6502 with 64K RAM.

Options:
- `-l FILE`: Load file at address `$0000`.
- `-r FILE`: Load ROM image at top of address space and reset into it.
- `-g ADDR`: Goto _ADDR_ after loading files.
- `-i ADDR`: Location of TTY input register `getc` (default `0xf004`)
- `-o ADDR`: Location of TTY ouput register `putc` (default `0xf001`)

Addresses given on the command line use C/Python base notation (`10`,
`0xa`, `012`) rather than the `+$` notation used with monitor
commands.

__[Command][py65-cmds] summary__ (similar to [VICE monitor][vice-mon]):

General:
- Readline command line editing available.
- Prefix numbers w/`$+%` for hex/decimal/binary. `radix` shows/sets default.
- `help [CMD]` with for more details.
- `quit`
- `add_label ADDR NAME`, `show_labels`, `delete_label NAME`: _NAME_ can be
  used in place of _ADDR_ below, and arithmetic (`start+8`) may be used.

Display and input:
- `~ NUMBER`: Displays _NUMBER_ in all bases.
- `registers`: display `PC  AC XR YR SP NV-BDIZC`.
  Set regs with `NAME=VALUE`, comma-separated.
- `mem START:END`: Display memory. Show 16-byte lines with `width 70`.
- `fill ADDR[:END] BYTE ...`: Deposit byte(s) starting at _ADDR_.
   Repeats bytes to _END_ if given.
- `disassemble START:END`
- `assemble ADDR [STMT]`: Interactive if no stmt given. Labels may be used.
- `load "FNURL" ADDR`: Load file or URL (quotes optional) at given
  address (`top` for top of memory). (Warning: C64 files will have a
  two-byte load address at the start of the file that's treated as data.)
- `save FNAME START END`

Execution:
- `reset`: Reset CPU and clear memory.
- `goto ADDR`: Set PC and resume execution
- `return`: Execute, return to monitor just before next `RTS/RTI`.
- `step`: Executes instr, disassembles next instr.
- `add_breakpoint ADDR`, `show_breakpoints`, `delete_breakpoint ADDR`.
- `cycles`: Display number of cycles since last reset.


Contact Information
-------------------

The author of this tool is Curt Sampson; the best ways to contact him are:
- [Telegram]: `@cjs_cynic`
- [Discord]: `0cjs`
- E-mail: <cjs@cynic.net>



<!-------------------------------------------------------------------->
[ASxxxx]: http://shop-pdp.net/ashtml/asxxxx.htm
[LinApple]: https://github.com/linappleii/linapple
[asl]: http://john.ccac.rwth-aachen.de:8000/as/
[dos33fsprogs]: https://github.com/deater/dos33fsprogs
[py65]: http://py65.readthedocs.org/
[pytest]: https://github.com/0cjs/sedoc/blob/master/lang/python/test/pytest.md
[retroabandon/osimg]: https://gitlab.com/retroabandon/osimg.git

[`README.md`]: README.md
[`Test`]: Test
[`bin/`]: bin/
[`doc/setup.md`]: ./doc/setup.md
[`exe/`]: exe/
[`lib/testmc/`]: lib/testmc/
[`pactivate`]: https://github.com/0cjs/pactivate
[`requirements.txt`]: requirements.txt
[`src/`]: src/
[`tmp/`]: tmp/
[`tool/`]: tool/

[VICE]: https://vice-emu.sourceforge.io/
[py65-cmds]: https://py65.readthedocs.io/en/latest/index.html#command-reference
[py65-src]: https://github.com/mnaberez/py65
[vice-mon]: http://vice-emu.sourceforge.net/vice_12.html

[Discord]: https://discord.com/
[Telegram]: https://telegram.org/
