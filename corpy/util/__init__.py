"""Small utility functions.

"""
from pprint import pprint


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
