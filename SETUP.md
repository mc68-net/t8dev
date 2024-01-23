t8dev Setup
===========

To set up a new repo to use t8dev, you need to do the following:

1. Create a top-level `Test` script that will call `t8dev` to do the setup
   and build. This is typically Bash (where `set -eu -o pipefail` is
   recommended), but can be any other language that can run programs.
2. Optional: check that your git submodules have been initialized. See
   `check_submodules()` in `Test`.
3. Strongly recommended: set variables for `T8_PROJDIR` (usually the root
   directory of your repo) and `t8dev` pointing to the `t8dev/bin/t8dev`
   program. These locations are referenced by these names below.
   (Information on the various paths used by `t8dev` is in
   `…/t8dev/pylib/t8dev/path.py`.) Export `T8_PROJDIR` to an environment
   variable of that name.
4. Add `$T8_PROJDIR/requirements.txt` with a list of Python modules used by
   t8dev (see the file here for a list) plus any others you want in the
   virtual environment.
5. Add a top-level `conftest.py` containing `from pytest_pt import *` to
   add the plugin that discovers `.pt` files in this repo containing unit
   tests. Add an `src/conftest.py` containing `from cjs8bitdev.src.conftest
   import *` to bring in the unit test framework for assembler code. (The
   path here will change when that code is moved to t8dev.)
6. Source `…/pactivate -B $T8_PROJDIR` to install (if necessary) and set up
   the Python virtual environment. Do not use the `-b` option to specify a
   different build directory; `t8dev` currently supports only
   `$T8_PROJDIR/.build/`.
7. Run `$t8dev buildtoolset asl` to build The Macroassembler AS and
   similar commands to have `t8dev` build any other tools you need that it
   knows how to build. (You can also use tools that are in your existing
   system path.)
8. Run `$t8dev aslauto exe/ src/` or similar to discover and build source
   files that have `.pt` unit test cases that load them. (The details of
   how this works are yet to be documented.)
9. Run `$t8dev asl` with parameters for all the files that do not have
   unit test cases. (These are typically top-level files that integrate
   code from the modules under `$T8_PROJDIR/src/` via `include` statements
   to produce an executable for a particular platform.)

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
