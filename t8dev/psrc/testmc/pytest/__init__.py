''' Standard testmc pytest support. This brings in the standard assertion
    introspection hook for testmc objects (overriding any previous
    `pytest_assertrepr_compare` hook) and all of the standard fixures. It's
    intended to be used with the following your ``conftest.py``:

        from    testmc.pytest  import *

    If you need your own introspection hook, you can (re-)define it after
    doing the import above, or do your own more customised imports. You'll
    want to see the documentation in the `testmc.pytest.assertrepr` module
    for more details.
'''

from    testmc.pytest.assertrepr  import pytest_assertrepr_compare
from    testmc.pytest.fixtures  import *
