"""Small utility functions.

"""
import inspect
import builtins
from pprint import pprint
from contextlib import contextmanager
from typing import Optional, Iterable


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
    blacklist: Optional[Iterable[str]] = None,
    whitelist: Optional[Iterable[str]] = None,
    restore_builtins: bool = True,
    keep_callables: bool = True,
    keep_upper: bool = True,
    keep_dunder: bool = True,
    keep_sunder: bool = False,
):
    """Run a block of code in a sanitized global environment.

    This is useful e.g. for testing answers in student assignments, because it
    will ensure that functions which accidentally capture global variables
    instead of using arguments fail. By default, it also restores overwritten
    builtins. The original environment is restored afterwards.

    :param blacklist: A list of global variable names to always remove,
        irrespective of the other options.
    :param whitelist: A list of global variable names to always keep,
        irrespective of the other options.
    :param restore_builtins: Make sure that the conventional names for built-in
        objects point to those objects (beginners often use ``list`` or
        ``sorted`` as variable names).
    :param keep_callables: Keep variables which refer to callables.
    :param keep_upper: Keep variables with all-uppercase identifiers
        (underscores allowed), which are likely to be intentional global
        variables (constants and the like).
    :param keep_dunder: Keep variables whose name starts with a double
        underscore.
    :param keep_sunder: Keep variables whose name starts with a single
        underscore.

    """
    blacklist, whitelist = set(blacklist or ()), set(whitelist or ())
    bw_intersection = blacklist & whitelist
    if bw_intersection:
        raise ValueError(f"Blacklist and whitelist overlap: {bw_intersection}")

    # this parent frame is in contextlib, the grandparent frame should be the
    # code that called `with clean_env(): ...`
    globals_to_prune = inspect.currentframe().f_back.f_back.f_globals
    pruned_globals = {}
    # NOTE: We'll be updating the globals dict as part of the loop, so we need
    # to store the items in a list, otherwise our iterator would be invalidated
    # by the update.
    for name, value in list(globals_to_prune.items()):
        remove, restore = True, False
        builtin = getattr(builtins, name, None)

        if name in blacklist:
            pass
        elif name in whitelist:
            remove = False
        elif restore_builtins and builtin is not None:
            restore = True
        elif keep_callables and callable(value):
            remove = False
        elif keep_upper and name.isupper():
            remove = False
        elif keep_dunder and name.startswith("__"):
            remove = False
        elif keep_sunder and name.startswith("_"):
            remove = False
        else:
            pass

        if remove:
            del globals_to_prune[name]
            pruned_globals[name] = value

        if restore:
            globals_to_prune[name] = builtin

    try:
        yield
    finally:
        globals_to_prune.update(pruned_globals)
