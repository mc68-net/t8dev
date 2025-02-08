Setting Up a Project to Use t8dev
=================================

To set up a new repo to use t8dev, you need a top-level test script
(usually called `Test`) that sets up t8dev, does the build, and runs your
tests. t8dev currently supports only Bash for this script, though it's
possible (with some work) to use other languages.

The root directory of your project is referred to as `T8_PROJDIR`; all
paths given below are relative to this unless otherwise specified.

#### Configuration Files

- `.gitignore` should contain `__pycache__/`, `/.build/` and `/.download/`.
- `requirements.txt` is optional, but may contain a list of Python modules
  used by your system. Often this is unused; the setup script (below) will
  install `t8dev[all]` which will bring in all the standard dependencies
  used by people developing with t8dev (`pytests`, `requests`, `py65`, etc.)
- `conftest.py` should contain `from pytest_pt import *` to add the pytest
  plugin that discovers unit-test `.pt` files in this repo.
- `src/conftest.py` should contain `from testmc.conftest import *` to bring
  in the unit test framework for assembler code.

#### t8dev

The [t8dev] package must currently be added a submodule of your repo:

    git submodule add add https://github.com/mc68-net/t8dev.git

Its [r8format] dependency may also be installed as a submodule if you
wish to edit it (i.e., do development work on it), but it will be
installed automatically from PyPI if not.

#### Top-level Test Script

Create `Test` in the root directory of your project, mark it executable,
and start with the following contents.

    #!/usr/bin/env bash
    set -Eeuo pipefail       # optional, but error-checking helps

    export T8_PROJDIR=$(cd "$(dirname "$0")" && pwd -P)
    t8dir=tool/t8dev    # or whatever your submodule path is
    [[ -r $T8_PROJDIR/$t8dir/t8setup.bash ]] \
        || git submodule update --init "$T8_PROJDIR/$t8dir"
    . "$T8_PROJDIR"/$t8dir/t8setup.bash

Further information on this is in the header comments of
[`t8setup.bash`](../t8setup.bash).

#### Building Tools and Running Tests

- Run your top-level `Test` script to ensure that the basic setup has been
  done.
- If you're working interactively at the command line, you'll need to
  activate your environment. This is done exactly as it is in the `Test`
  script: set the `T8_PROJDIR` variable in your shell and sourcing the
  environment setup script: `. t8dev/t8setup.bash`. (If you're adding
  code to the setup script, this is obviously already done at the top.)
- Run `t8dev buildtoolset asl` to build The Macroassembler AS and similar
  commands to have `t8dev` build any other tools you need that it knows how
  to build. (You can also use tools that are in your existing system path.)
- Run `t8dev aslauto exe/ src/` or similar to discover and build source
  files that have `.pt` unit test cases that load them. (The details of how
  this works are yet to be documented.)
- Run `t8dev asl` with parameters for all the files that do not have unit
  test cases. (These are typically top-level files that integrate code from
  the modules under `$T8_PROJDIR/src/` via `include` statements to produce
  an executable for a particular platform.)



<!---------------------------------------------------------------------------->
[r8format]: https://github.com/mc68-net/r8format
[t8dev]: https://github.com/mc68-net/t8dev
