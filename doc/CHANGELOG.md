Changelog
=========

This file follows most, but not all, of the conventions described at
[keepachangelog.com]. Especially we always use [ISO dates]. Subsections or
notations for changes may include Added, Changed, Deprecated, Fixed,
Removed, and Security.

Release version numbers follow the [Python packaging
specifications][pyver], which are generally consistent with [semantic
versioning][semver]: are _major.minor.patch_ Development versions use the
version number of the _next_ release with _.devN_ appended; `1.2.3.dev4` is
considered to be earlier than `1.2.3`.

On any change to the programs or libraries (not, generally, the tests), the
previous release version number is bumped and `.devN` is appended to it, if
this hasn't already been done. A `.devN` suffix will stay until the next
release, though its _N_ need not be bumped unless the developer feels the
need.

Releases are usually tagged with `vN.N.N`. Potentially not all releases
will be tagged, but specific releases can also be fetched via the Git
commit ID.

For release instructions, see [cynic-net/pypi-release] on GitHub.


### dev

### 01.2. (2024-10-24)
- Fixed: t8setup.bash no longer adds `[all]` to local `t8dev` install

### 0.1.1 (2024-10-24)
- Changed: No more need for `t8dev[all]`; all optional req's now standard.
- Added: iomem now throws an exception if an I/O function attached to a
  memory addess returns a bad value (not int or int out of range) on read.
- Fixed: tmc now returns exitvalue if exitport is read so that the
  command-line simulator doesn't die if you read that address.

### 0.1.0 (2024-10-20)
- Breaking API change: testmc.pytest.fixtures.loadbios() now does not
  require (though still can optionally accept) a BIOS name. See commit
  messge for full details.

### 0.0.6 (2024-10-20)
- Fixed: mos65 simulator throws ModuleNotFoundError for py65 only if it's
  actually used. (This fixes `t8dev[toolset]` and similar installs.)

### 0.0.5 (2024-10-20)
- Added: Simulator/unit test BIOS source code and `t8dev aslt8dev` command
- Added: `tmc` program for command line simulation of any CPU simulator,
  replacing `tmc6800` which did only mc6800 simulation.
- Changed: `tmc` simulator now uses output to a port to request exit.
- Updated: New version of `bm2` Basic Master Jr. emulator
  (old version no longer downloadable from that site).
- Added: Shell scripts from `bin/` added to distribution package.
- Added: bin/cmpasl script to assemble a disassembled binary and compare
  with the original

### 0.0.4 (2024-09-22)
- Fixed: `t8dev emu` no longer tries to use `wine` on Windows

### 0.0.3 (2024-08-28)
- Fixed: The locations whence to download TK-80BS ROM images have changed.
- Changed: The `pytest_pt` module is no longer included under `psrc/`;
  instead it's now a runtime dependency. (See `pyproject.toml` for an
  explanation of why it's a runtime instead of development dependency.)
- Changed: When building ASL from `asl-releases`, use branch `upstream`
  instead of `dev/cjs/master`; thus you now always get the latest version.
  (There is currently no facility to request an earlier version except to
  tweak the source code.)

### 0.0.2 (2024-07-30)
- Added: CSCP emulator suite `tk80bs` ROM configuration (BASIC SYSTEM) and
  `tk80` alternate ROM configuration (base system).
- Fixed: Various `t8dev emulator cscp` UI improvements.

### 0.0.1 (2024-07-21)
- Added: `t8setup.bash` can now be run without setting $T8_PROJDIR if the
  current or higher directory appears to have a virtualenv with t8dev
  installed.
- Changed: Use Python packaging dependency management so that the
  user no longer needs to put t8dev dependencies in `requirements.txt`.
- Added: Add [CSCP] emulators to toolsets.
- Added: `t8dev emulator` command.

### 0.0.0 (2024-04-23)
- Initial PyPI release for testing; proper documentation not available.



<!-------------------------------------------------------------------->
[ISO dates]: https://xkcd.com/1179/
[cynic-net/pypi-release]: https://github.com/cynic-net/pypi-release
[keepachangelog.com]: https://keepachangelog.com/
[pyver]: https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers
[semver]: https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning

[CSCP]: http://takeda-toshiya.my.coocan.jp/common/
