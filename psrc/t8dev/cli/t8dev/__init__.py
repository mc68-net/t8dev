#!/usr/bin/env python3
'''
    t8dev - build tool for retro 8-bit cross-development

    The t8dev directory may be placed anywhere; ``t8dev`` uses its own
    path to find its modules. See the `t8dev.path` module documentation
    for information about the project directory structure and how the
    ``T8_PROJDIR`` environment variable is used. In particular, t8dev will
    always use tools from `path.tooldir('bin/')`, if available, in
    preference to any others.

    TODO:
    • t8dev should build project project-local tools into
      ``BASEDIR/.build/tool/``.

'''

# N.B. for developers:
# • In the long run we want nicer error messages, but for the moment
#   developers can easily enough work out the problem from the exception.
# • Older systems still supply Python 3.5. To try to remain compatible,
#   always use str() when passing path-like objects to standard library
#   functions.

from    t8dev.cli.t8dev.main  import main
