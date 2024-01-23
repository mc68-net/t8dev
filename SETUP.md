t8dev Setup
===========

To set up a new repo to use t8dev, you need a top-level test script
(usually called `Test`) that sets up t8dev, does the build, and runs your
tests. t8dev currently supports only Bash for this script, though it's
possible (with some work) to use other languages.

#### Test Setup

Create `Test` at the top of your project, mark it executable, and start it
with:

    #!/usr/bin/env bash
    set -euo pipefail       # optional, but error-checking helps

    export T8_PROJDIR=$(cd "$(dirname "$0")" && pwd -P)
    . "$T8_PROJDIR"/t8dev/project-setup.bash

This will:
- Check that $T8_PROJDIR is set.
- Check that your submodules have been initialised.
- Process any `-c` (clean build) and `-C` (very clean build) arguments at
  the front of the arguments list.
- Create (if necessary) and activate the Python virtual environment.

#### Additional Files

- `$T8_PROJDIR/requirements.txt` should contain a list of Python modules
  used by your system and t8dev. Typically this will include `requests`,
  `pytest`, and `py65@git+https://github.com/mnaberez/py65.git`.
- `$T8_PROJDIR/conftest.py` should contain `from pytest_pt import *` to add
  the pytest plugin that discovers unit-test `.pt` files in this repo.
- `src/conftest.py` should contain `from testmc.conftest import *` to bring
  in the unit test framework for assembler code.

#### Building Tools and Running Tests

- Run `$t8dev buildtoolset asl` to build The Macroassembler AS and similar
  commands to have `t8dev` build any other tools you need that it knows how
  to build. (You can also use tools that are in your existing system path.)
- Run `$t8dev aslauto exe/ src/` or similar to discover and build source
  files that have `.pt` unit test cases that load them. (The details of how
  this works are yet to be documented.)
- Run `$t8dev asl` with parameters for all the files that do not have unit
  test cases. (These are typically top-level files that integrate code from
  the modules under `$T8_PROJDIR/src/` via `include` statements to produce
  an executable for a particular platform.)


Other Notes
-----------

These notes are taken from the `Test` script of another repo; they
are a partial to-do list for t8dev.

XXX It would be nice to be able here to build the unit test versions of
source under 8bitdev/. However, there are two path issues that need to
be resolved to do this:
1. The tests (.pt files) underneath 8bitdev/src/ assume that 8bitdev/
   is in the Python import search path so they can import common test
   code. This is true when building with 8bitdev/ as the project
   directory, but not with a different project directory. This could be
   hacked in with `export PYTHONPATH=$T8_PROJDIR/8bitdev/`,
   though that may not be the best solution.
2. The tests specify the object files to be built and loaded using
   paths that implicitly give the source file relative to 8bitdev/,
   e.g. `src/mc68/simple.p` However, here they are relative to
   $T8_PROJDIR, e.g. `$T8_PROJDIR/8bitdev/src/mc68/simple.a65`. It's
   not clear if it's worth trying to change the system to handle things
   being built from different locations due to different settings of
   $T8_PROJDIR.
For the moment, at least, we just assume that everything under 8bitdev/
is already tested and working and have our programs here include this
presumably-tested-and-working source.

XXX There are some cases where we want to run programs that load object
files built from source files under 8bitdev. One example is bin/tmc6800,
which wants to load $BUILD/obj/src/tmc68/bioscode.p along with whatever
object file the user wants to run. We can't even build
8bitdev/src/tmc68/bioscode.a65 because it includes `src/tmc68/bios.a68`,
which is actually under $T8_PROJDIR/8bitdev/, not $T8_PROJDIR/, and so is
not in the ASL include search path.

One part of the solution may be to have a way of specifying additional
include search paths for ASL (and other tools), probably with a -I
option to t8dev. However, that doesn't deal with the issue that
bin/tmc6800 is looking for the BIOS object file in obj/src/…, not
obj/8bitdev/src/…. We could hack around this by also adding an option
to bin/tmc6800 to tell it what BIOS to load (or just allow
specification of multiple objects to load and skip the standard BIOS
when given multiple object files), but it's not clear that this is the
best or most general solution to the problem. Possibly a clever way of
resolving the test issue above could also deal with this.

An issue with trying to run

    $t8dev asl 8bitdev/src/tmc68/bioscode.a65

XXX Actually, the real issue exposed above is that bin/tmc6800 is part
of t8dev (it runs t8dev's Python 6800 simulator) but it's got a
dependency on code that's part of 8bitdev (src/tmc68/bioscode). Adding
assembly source to t8dev is awkward and doesn't actually seem entirely
correct. Possibly the BIOS to load (if any) should be specified in a
per-project configuration file?

<!---------------------------------------------------------------------------->
[8bitdev]: https://github.com/0cjs/8bitdev
