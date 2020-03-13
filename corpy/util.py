"""Small utility functions.

"""
from pprint import pprint
from contextlib import contextmanager


def _head_gen(items, first_n):
    for idx, item in enumerate(items):
        if first_n == idx:
            break
        yield item


def head(collection, first_n=None):
    """Inspect `collection`, truncated if too long.

    If ``first_n=None``, an appropriate value is determined based on the type
    of the collection.

    """
    type_ = type(collection)
    if first_n is None:
        if type_ in (str, bytes):
            first_n = 100
        else:
            first_n = 10
    if len(collection) <= first_n:
        pprint(collection)
        return
    if type_ == str:
        constructor = "".join
    elif type_ == bytes:
        constructor = b"".join
    else:
        constructor = type_
    items = collection.items() if hasattr(collection, "items") else collection
    pprint(constructor(_head_gen(items, first_n)))


def cmp(lhs, rhs, test="__eq__"):
    """Wrap assert statement to automatically raise an informative error."""
    msg = f"{head(lhs)} {test} {head(rhs)} is not True!"
    ans = getattr(lhs, test)(rhs)
    # operators automatically fall back to identity comparison if the
    # comparison is not implemented for the given types, magic methods don't →
    # if comparison is not implemented, we must fall back to identity
    # comparison manually, because NotImplemented is truthy and makes the
    # assert succeed
    if ans is NotImplemented:
        ans = lhs is rhs
    assert ans, msg


@contextmanager
def clean_env(
    *,
    blacklist=None,
    whitelist=None,
    keep_dunder=True,
    keep_callables=True,
    keep_sunder=False,
):
    """Run a block of code in a sanitized global environment.

    This is useful e.g. for testing answers in student assignments,
    because it will ensure that functions which accidentally capture
    global variables instead of using arguments fail.

    By default, global variables starting with a double underscore and
    callables are kept. A whitelist of additional variables to keep can
    also be provided. The environment is restored afterwards.

    """
    if blacklist and whitelist:
        raise ValueError("Only one of blacklist or whitelist can be specified.")

    hidden_globs = {}
    if blacklist:
        for name in blacklist:
            value = globals().pop(name)
            hidden_globs[name] = value
    else:
        for name, value in list(globals().items()):
            is_dunder = name.startswith("__")
            if not (
                (keep_dunder and is_dunder)
                or (keep_callables and callable(value))
                or (keep_sunder and name.startswith("_") and not is_dunder)
                or (whitelist and name in whitelist)
            ):
                del globals()[name]
                hidden_globs[name] = value

    try:
        yield
    finally:
        globals().update(hidden_globs)
