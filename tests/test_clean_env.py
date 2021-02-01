import pytest

from corpy.util import clean_env


def test_blacklist_works():
    globals().update(__dunder=1)
    with clean_env():
        assert globals().get("__dunder") == 1
    with clean_env(blacklist=["__dunder"]):
        assert globals().get("__dunder") is None


def test_whitelist_works():
    globals().update(foo=1)
    with clean_env():
        assert globals().get("foo") is None
    with clean_env(whitelist=["foo"]):
        assert globals().get("foo") == 1


def test_blacklist_cannot_overlap_with_whitelist():
    with pytest.raises(ValueError) as err:  # type: ignore
        with clean_env(blacklist=["foo", "bar"], whitelist=["bar", "baz"]):
            pass
    assert str(err).endswith("{'bar'}")


def test_reassigned_builtins_are_restored():
    globals().update(sorted=None)
    assert not callable(sorted)
    with clean_env():
        assert callable(sorted)
    assert not callable(sorted)


def test_strict():
    global foo
    foo = ()

    def return_foo():
        return foo

    with clean_env(strict=False):
        assert foo == ()
    with pytest.raises(NameError) as err:  # type: ignore
        with clean_env(strict=False):
            return_foo()
    assert "'foo'" in str(err)


def test_modules():
    with clean_env():
        assert globals().get("pytest") is pytest
    with clean_env(modules=True):
        assert globals().get("pytest") is None


def test_callables():
    foo = lambda x: x
    globals().update(foo=foo)
    with clean_env():
        assert globals().get("foo") is foo
    with clean_env(callables=True):
        assert globals().get("foo") is None


def test_upper():
    globals().update(FOO_BAR=1)
    with clean_env():
        assert globals().get("FOO_BAR") == 1
    with clean_env(upper=True):
        assert globals().get("FOO_BAR") is None


def test_dunder():
    globals().update(__dunder=1)
    with clean_env():
        assert globals().get("__dunder") == 1
    with clean_env(dunder=True):
        assert globals().get("__dunder") is None


def test_sunder():
    globals().update(_sunder=1)
    with clean_env(sunder=False):
        assert globals().get("_sunder") == 1
    with clean_env():
        assert globals().get("_sunder") is None


def test_can_be_used_as_decorator():
    global foo, FOO
    foo = FOO = ()

    @clean_env()
    def return_foo():
        return foo

    @clean_env()
    def return_FOO():
        return FOO

    with pytest.raises(NameError) as err:  # type: ignore
        assert return_foo() is foo
    assert "'foo'" in str(err)
    assert return_FOO() is FOO
