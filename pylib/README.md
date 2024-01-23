t8dev Python Libraries
======================

This `pylib/` subdirectory contains all of the various Python libraries
that come with t8dev, including CPU simulators and the like.

Command-line Python programs that use `t8dev.path.b8home()` or related
functions must ensure that `__main__.B8_HOME` is set to the path to the
t8dev top-level directory (the directory just above this one). Doing this
is usually a natural part of finding this library directory and adding it.
t8dev command-line programs in `bin/` do the following:

    B8_HOME = dirname(dirname(abspath(__file__)))
    addsitedir(os.path.join(B8_HOME, 'pylib'))

Many functions also expect the environment variable `T8_PROJDIR` to be set
to point to the project directory (the build directory and the like reside
under this). See the `t8dev.path` module for more details.
