r8format TODO List
==================

#### High Priority

- Convert the functional tests in `Test` to use pytest so that they become
  part of the t8dev default test suite when this is a subrepo in a project
  using t8dev.
- Document in the README the top-level import packages in this distribution
  package. (Currently only the bin/* files are documented.)

#### Low Priority

- Consider whether the command-line programs should have a `--version`
  option. If we do this, we need somehow to synchronise the version between
  `pyproject.toml` and the programs.

#### BASIC Tokenisation

- TRS-80 CoCo and MC-10 tokenisation [info][mc10emu]. (The MC-10 emulator
  contains a CoCo → MC-10 token converter.)



<!-------------------------------------------------------------------->
[mc10emu]: https://bitbucket.org/camennie/mc10-emulator/src/master/
