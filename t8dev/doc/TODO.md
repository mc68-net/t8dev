To-do List
==========

#### Documentation
- Move most of the stuff in `README.md` into appropriate files under `doc/`
  and then add `readme = 'README.md'` to the `pyproject.toml`.
- Consider whether we should add some sort of [pydoc] support, which might
  be useful for bringing up API docs in an editor the way `K` does in Vim.
- Have a look at [Sphinx][] (combined with MyST for Markdown support?),
  which would let us have documentation on [readthedocs.org].

[pydoc]: https://docs.python.org/3/library/pydoc.html
[Sphinx]: https://www.sphinx-doc.org/
[readthedocs.org]: https://readthedocs.org/

#### Cleanup

- scr/tmc68/biocode: use `ds prchar-$` (current PC) to org routine locations
- Make a better `repr()`/`str()` for `testmc.generic.Machine` so that
  `assert R(...) = m.regs` looks nicer (and maybe provides useful info).
- testmc.generic.machine.Machine.load_memimage() currently sets the
  PC to `None` if there's no entrypoint in the file it's loading. It
  should probably instead set the PC to the reset vector, or the first
  address loaded, or something like that.

#### Setup

- `t8dev` currently must be a submodule because the `t8setup.bash` script,
  `pactivate`, and anything else it may one day require (e.g. as template
  files) is not in the built Python distribution package. Ideally a
  developer should be able just to add `t8dev` to her `requirements.txt`,
  but this creates a bootstrap problem. Perhaps this could be worked around
  with a downloadable bootstrap script that could be added to the
  developer's repo, which would be able to fetch the bare minimum it needs
  into `.build/bootstrap/t8dev/` and build an environment from there.

#### Build/Test System Fixes

- extract src/mc68/{hello,cjsmon} loadbios() to test framework
- remove more `  cpu 6502` from files and put in unit test framework?
- Rewrite Test in Python and replace UNIT_TESTING symbol per comments.

#### Features

- Add the `testmc.generic.IOMem` interface to `testmc.mos65`.
- Add "hexadecimal integers" to framework with `__repr__()`s that
  print as `$EA` or `$FFFF`. Construct perhaps with `A(0xFFFF)`
  (address) and `B(0xFF)` (byte)?
- "Omniscient debugging"; dump initial memory and symbol table to a
  file, followed by a trace of full execution (instruction, resulting
  register values and the memory change for each step) of a call.
  Probably also want a tool that can dump arbitrary memory at any step.

#### Third-party Tool Support

- Figure out a convenient but quiet way to somehow inform the user of
  which tools he's using, particularly system-supplied vs. .build/.
- Allow configuring tools as "dontuse," w/no build or install, and
  code that needs the tools simply not being built.

#### Third-party Tools to Consider Using

- Use [omni8bit](https://github.com/robmcmullen/omni8bit) (`pip
  install omni8bit`) front end for emulator startup/run here?
- Look into [Omnivore](https://github.com/robmcmullen/omnivore) (`pip
  install omnivore`), a visual tool providing tools and front-ends for
  toher tools: various emulators w/debuggers; binary editor;
  disassemblers; ATasm 6502 cross-assembler; graphics and map editors.
