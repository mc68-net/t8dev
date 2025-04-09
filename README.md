8-bit Development Project Packages
==================================

This repo is the home of Python packages providing support for development
on 8-bit (and some 16-bit) Japanese and Western vintage computers and
gaming consoles such as the Apple II, NEC PC-8001 and Commodore 64 (and
many more).

- [r8format]: Retrocomputing 8-bit file format manipulation tools
- [t8dev]: Tools for 8-bit cross-development

Usage
-----

A minimal example of using t8dev can be found in the [sample-t8dev-project]
repository; a much larger and more complex example is Curt J. Sampson's
[8bitdev] repo.

### Typical Usage

For typical usage, simply install the [`t8dev`] package from the [Python
Package Index][PyPI]; this can be done with `pip install t8dev`. (This will
automatically bring in [`r8format`] and other dependencies.) You can then
run the top-level `Test` script in [sample-t8dev-project] to confirm that
it's working.

If you're familiar with [`virtualenv`], it's usually easier to install
`t8dev` into a project-local virtualenv. [pactivate] can be helpful for
this; simply drop the [pactivate script] into the root of your project
directory, add `t8dev` to your `requirements.txt`, and add `source
./pactivate` to your test script (or just source it at the command line).

Before running `t8dev` or other programs, you will need to set the
`T8_PROJDIR` environment variable to point to the root directory of your
project. (This is where the `.build/` directory, containing the tools that
t8dev builds, test artifacts and other information will be placed.)

Note that in neither case will the third-party tools directory,
`.build/tool/bin/`, be added to your path. The `t8dev` program will
automatically find tools in this path, but if you wish to run them directly
you will need to add that directory to your own $PATH, in your test script,
at the command line, or both.

### Development Usage

If you are modifying the `t8dev` and/or `r8format` packages, or just want
to run their tests, the easiest way to set this up is to clone this entire
repo under your project dir, typically as a submodule, using one of the
following two commands:

    git clone https://github.com/mc68-net/t8dev.git
    git submodule add t8dev https://github.com/mc68-net/t8dev.git

Then add the following to your `requirements.txt` (or manually run `pip
install` with the arguments below) to install the packages in editable
mode:

    -e t8dev/r8format/
    -e t8dev/t8dev/

You can then use the packages as above, but an easier way to get set up is
to  `T8_PROJDIR`, export it and `source t8dev/t8dev/t8setup.bash`, which
will set up a project-local virtualenv, add various `bin/` directories to
your path, ensure that submodules are updated, and so on. It also will
parse "$@" for `-C` (big clean) and `-c` (little clean) options at the
start of the command line to clean all or part of `$T8_PROJDIR/.build/`.

That `source` command is typically placed in a top-level test script, as
described in the comments at the head of [`t8setup.bash`], but can also be
used directly from the command line (but remember to export `T8_PROJDIR`
first).

### Upgrading Old Clients

If you are currently using separate `r8format/` and `t8dev/` Git
submodules, you should:
- `git rm r8format/`;
- Update `t8dev/` to the head of `main`;
- Clean up any old directory trees lying around, such as `t8dev/psrc/`
  (which moved to `t8dev/t8dev/src/`);
- Update your `requirements.txt` per the §"Development Usage" above;
- Rebuild and test, using `-C` (or any other equivalant to `rm -rf
  .build/`); and
- Commit your changes.


Support
-------

Support information depends on the particular package with which you're
having issues or have questions. See the `*/README.md` files in the
subdirectories for further information.



<!-------------------------------------------------------------------->

<!-- Packages within this repo. -->
[`r8format`]: https://pypi.org/project/r8format/
[`t8dev`]: https://pypi.org/project/t8dev/
[r8format]: ./r8format/
[t8dev]: ./t8dev/
[`t8setup.bash`]: https://github.com/mc68-net/t8dev/blob/main/t8dev/t8setup.bash

<!-- Projects using t8dev. -->
[8bitdev]: https://github.com/0cjs/8bitdev.git
[sample-t8dev-project]: https://github.com/mc68-net/sample-t8dev-project.git

<!-- External packages and other links. -->
[PyPI]: https://pypi.org
[`virtualenv`]: https://pypi.org/project/virtualenv/
[pactivate]: https://github.com/cynic-net/pactivate
[pactivate script]: https://raw.githubusercontent.com/cynic-net/pactivate/refs/heads/main/pactivate
