''' The testmc tests themselves use the standard testmc pytest support.

    This file also used to be the source of hooks and fixtures: projects
    using testmc would ``from testmc.conftest import *``. That's obviously
    not a great idea (in case testmc needs anything special here), and so
    that's now all been moved to `testmc.pytest`, imported with ``from
    testmc.pytest import *``. However, for the moment, importing from here
    will also still work.
'''

from    testmc.pytest  import *
