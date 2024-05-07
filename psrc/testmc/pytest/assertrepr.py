''' Nicer assertion error display for testmc objects.

    This displays, e.g. register objects in a nice above/below format,
    It's generally used by all projects using t8dev (as well as t8dev
    itself). Typically you won't import from this but instead bring it and
    everything else in with the following in your ``conftest.py``:

        from    testmc.pytest  import *

    If you have your own `pytest_assertrepr_compare` hook, you should
    directly import `assertrepr_compare` from this and call it after you do
    your own checks for objects that should display differently in
    assertion failures.

    By default this does not import the `pytest_assertrepr_compare` hook
    when you ``import *`` from this module; if you want the standard
    envirionment, you should instead ``from testmc.pytest import *``.

    For more details on the `pytest_assertrepr_compare` hook, see
    `Defining your own explanation for failed assertions`_ in the
    pytest documentation.

    .. Defining your own explanation for failed assertions: https://docs.pytest.org/en/stable/how-to/assert.html#defining-your-own-explanation-for-failed-assertions

'''

__all__ = ['assertrepr_compare']

from    testmc.generic      import GenericRegisters as GR

def assertrepr_compare(op, left, right):
    ''' Nicer assertion error displays for comparisons between testmc objects.

        This has the same parameters and return value (a sequence of `str`
        or `None`) as `pytest_assertrepr_compare`. You can include this in
        your own `pytest_assertrepr_compare` function, trying other formats
        if this returns `None`.
    '''
    if isinstance(left, GR) and isinstance(right, GR) and op == "==":
        return (
            'Unexpected {} values:'.format(right.__class__.__name__),
            repr(left), repr(right),
        )

def pytest_assertrepr_compare(op, left, right):
    ''' For `testmc` objects, override the standard pytest assertion
        comparison failure display. If you have other overrides as well,
        you probably want instead to import `assertrepr_compare()` and
        build your own version of this function.
    '''
    return assertrepr_compare(op, left, right)
