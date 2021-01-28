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


def test_keep_callables_works():
    foo = lambda x: x
    globals().update(foo=foo)
    with clean_env():
        assert globals().get("foo") is foo
    with clean_env(keep_callables=False):
        assert globals().get("foo") is None


def test_keep_upper_works():
    globals().update(FOO_BAR=1)
    with clean_env():
        assert globals().get("FOO_BAR") == 1
    with clean_env(keep_upper=False):
        assert globals().get("FOO_BAR") is None


def test_keep_dunder_works():
    globals().update(__dunder=1)
    with clean_env():
        assert globals().get("__dunder") == 1
    with clean_env(keep_dunder=False):
        assert globals().get("__dunder") is None


def test_keep_sunder_works():
    globals().update(_sunder=1)
    with clean_env(keep_sunder=True):
        assert globals().get("_sunder") == 1
    with clean_env():
        assert globals().get("_sunder") is None
