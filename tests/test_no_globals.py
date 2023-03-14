import pytest
from IPython.testing.globalipapp import start_ipython
from IPython.utils.capture import capture_output

from corpy.util import no_globals


@pytest.fixture(scope="module")
def module_ip():
    yield start_ipython()


@pytest.fixture(scope="function")
def ip(module_ip):
    module_ip.run_line_magic("load_ext", "corpy")
    module_ip.run_cell(
        """
foo = 1
def bar():
    print(foo)
"""
    )
    yield module_ip
    module_ip.run_line_magic("reset", "-f")


def test_blacklist_works():
    globals().update(__dunder=1)
    with no_globals():
        assert globals().get("__dunder") == 1
    with no_globals(blacklist=["__dunder"]):
        assert globals().get("__dunder") is None


def test_whitelist_works():
    globals().update(foo=1)
    with no_globals():
        assert globals().get("foo") is None
    with no_globals(whitelist=["foo"]):
        assert globals().get("foo") == 1


def test_blacklist_cannot_overlap_with_whitelist():
    with pytest.raises(ValueError) as exc_info:
        with no_globals(blacklist=["foo", "bar"], whitelist=["bar", "baz"]):
            pass
    assert exc_info.match(r"\{'bar'\}$")


def test_reassigned_builtins_are_restored():
    globals().update(sorted=None)
    assert not callable(sorted)
    with no_globals():
        assert callable(sorted)
    assert not callable(sorted)


def test_no_strict():
    global foo
    foo = ()

    def return_foo():
        return foo

    with no_globals(strict=False):
        assert foo == ()
    with pytest.raises(NameError) as exc_info:
        with no_globals(strict=False):
            return_foo()
    assert "'foo'" in exc_info.exconly()


def test_no_strict_only_prunes_globals_in_direct_children_of_calling_scope():
    # As in, if I call foo(), then only the global environment of foo should be
    # pruned (and of course, also that of any function which happens to share
    # the same environment, so typically all functions defined within the same
    # interactive session). By contrast, pruning the global environment of
    # functions from imported modules is generally undesirable. E.g. re.match
    # uses a global _cache -- we want that to remain accessible, flagging access
    # to this _cache as a mistake is spurious.
    import fake_re

    def func_i_wish_to_debug():
        fake_re.match()

    assert fake_re._cache
    with no_globals(strict=False):
        func_i_wish_to_debug()


def test_modules():
    with no_globals():
        assert globals().get("pytest") is pytest
    with no_globals(modules=True):
        assert globals().get("pytest") is None


def test_callables():
    foo = lambda x: x
    globals().update(foo=foo)
    with no_globals():
        assert globals().get("foo") is foo
    with no_globals(callables=True):
        assert globals().get("foo") is None


def test_upper():
    globals().update(FOO_BAR=1)
    with no_globals():
        assert globals().get("FOO_BAR") == 1
    with no_globals(upper=True):
        assert globals().get("FOO_BAR") is None


def test_dunder():
    globals().update(__dunder=1)
    with no_globals():
        assert globals().get("__dunder") == 1
    with no_globals(dunder=True):
        assert globals().get("__dunder") is None


def test_sunder():
    globals().update(_sunder=1)
    with no_globals(sunder=False):
        assert globals().get("_sunder") == 1
    with no_globals():
        assert globals().get("_sunder") is None


def test_can_be_used_as_decorator():
    global foo, FOO
    foo = FOO = ()

    @no_globals()
    def return_foo():
        return foo

    @no_globals()
    def return_FOO():
        return FOO

    with pytest.raises(NameError) as exc_info:
        assert return_foo() is foo
    assert "'foo'" in exc_info.exconly()
    assert return_FOO() is FOO


# We can't use pytest.raises in the IPython magic tests, in part because
# no_globals itself uses run_cell. It's that nested call that raises an error,
# which is then handled by the IPython shell, i.e. printed to stdout, at which
# point it's considered handled and it's not propagated further out into the
# outer run_cell call here in the test suite, so the result we get here looks as
# if there was no error.
#
# I could in theory call raise_error on the run_cell result in no_globals, but I
# would either have to detect running in a test scenario and only do it then, or
# I'd have to accept that this additional traceback pointing into the guts of
# corpy is shown to users every time no_globals does its job and catches access
# to a global, which is unacceptable. And I could *still* not just use
# pytest.raises, I'd have to manually call raise_error here in the test case as
# well, or test against the error_in_exec attribute of the result.
#
# So instead, we use capture_output to get a hold of the error message printed
# by IPython and run asserts against that, which is much less messy.
#
# For possible future reference: there's also a way to intercept exceptions by
# setting a custom handler:
#
#   ip.set_custom_exc((Exception,), lambda *a, **kw: None)
#
# We test both strict and non-strict modes, both in cell and line magic mode,
# because the code paths are different and the execution machinery tricky enough
# that it's worth it to basically duplicate tests for the same kind of
# functionality as above, to make sure that the IPython execution context
# doesn't break them.

FOO_NOT_DEFINED_ERR = (
    "\nNameError: global 'foo' exists but hidden by corpy.util.no_globals. "
    "Trying to access it may be a mistake? "
    "See: https://corpy.readthedocs.io/en/stable/guides/no_globals.html\n"
)


def test_cell_magic_strict(ip):
    with capture_output() as captured:
        ip.run_cell("%%no_globals\nprint(foo)")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr

    with capture_output() as captured:
        ip.run_cell("%%no_globals\nbar()")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr


def test_cell_magic_non_strict(ip):
    with capture_output() as captured:
        ip.run_cell("%%no_globals -X\nprint(foo)")
    assert captured.stdout == "1\n"
    assert not captured.stderr

    with capture_output() as captured:
        ip.run_cell("%%no_globals -X\nbar()")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr


def test_line_magic_strict(ip):
    with capture_output() as captured:
        ip.run_cell("%no_globals print(foo)")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr

    with capture_output() as captured:
        ip.run_cell("%no_globals bar()")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr


def test_line_magic_non_strict(ip):
    with capture_output() as captured:
        ip.run_cell("%no_globals -X print(foo)")
    assert captured.stdout == "1\n"
    assert not captured.stderr

    with capture_output() as captured:
        ip.run_cell("%no_globals -X bar()")
    assert captured.stdout.endswith(FOO_NOT_DEFINED_ERR)
    assert not captured.stderr
