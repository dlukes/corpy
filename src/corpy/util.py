"""Small utility functions.

"""
import sys
import inspect
import builtins
from pprint import pprint
from contextlib import contextmanager

from types import FrameType, GeneratorType
from typing import Optional, Iterable, Tuple


#
# ------------------------------------------------------------------------- Head {{{1


def _head_gen(items, first_n):
    for idx, item in enumerate(items):
        if first_n == idx:
            break
        yield item


def head(collection, first_n=None):
    """Inspect `collection`, truncated if too long.

    >>> head(list(range(1_000)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

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


#
# -------------------------------------------------------------------------- Cmp {{{1


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


#
# -------------------------------------------------------------------- Clean env {{{1


def _get_user_frame_and_generator(
    start_frame: FrameType,
) -> Tuple[FrameType, GeneratorType]:
    ctxlib_fname = generator = None
    # walk up the call stack, skipping frames in this file and in
    # contextlib, to reach the user code that triggered `with clean_env(): ...`
    # and whose globals we want to tamper with
    for frame_info in inspect.getouterframes(start_frame):
        if ctxlib_fname is None and frame_info.filename.endswith("contextlib.py"):
            ctxlib_fname = frame_info.filename
            generator = frame_info.frame.f_locals["self"].gen
        elif ctxlib_fname is not None and frame_info.filename != ctxlib_fname:
            break
    else:
        raise RuntimeError("User's frame not found in call stack")
    assert isinstance(generator, GeneratorType)
    return frame_info.frame, generator


@contextmanager
def clean_env(
    *,
    blacklist: Optional[Iterable[str]] = None,
    whitelist: Optional[Iterable[str]] = None,
    strict: bool = True,
    restore_builtins: bool = True,
    modules: bool = False,
    callables: bool = False,
    upper: bool = False,
    dunder: bool = False,
    sunder: bool = True,
):
    """Run a block of code in a sanitized global environment.

    A context manager which temporarily removes global variables from scope:

    >>> foo = 42
    >>> with clean_env():
    ...     foo
    ...
    Traceback (most recent call last):
      ...
    NameError: name 'foo' is not defined

    The original environment is restored at the end of the block:

    >>> foo
    42

    Also works as a decorator, which is like wrapping the entire function body
    with the context manager:

    >>> @clean_env()
    ... def return_foo():
    ...     return foo
    ...
    >>> return_foo()
    Traceback (most recent call last):
      ...
    NameError: name 'foo' is not defined

    By default, `clean_env` tries to be clever and leave e.g. functions alone,
    as well as other objects which are likely to be "legitimate" globals. It
    also restores overwritten builtins.

    This is useful e.g. for testing answers in student assignments, because it
    will ensure that functions which accidentally capture global variables
    instead of using arguments fail.

    :param blacklist: A list of global variable names to always remove,
        irrespective of the other options.
    :param whitelist: A list of global variable names to always keep,
        irrespective of the other options.
    :param strict: In non-strict mode, allow global variables in the current
        scope, i.e. only start pruning within function calls. NOTE: This is
        slower because it requires tracing the function calls. Also, when using
        `clean_env` as a function decorator, non-strict probably doesn't make
        sense.
    :param restore_builtins: Make sure that the conventional names for built-in
        objects point to those objects (beginners often use ``list`` or
        ``sorted`` as variable names).
    :param modules: Prune variables which refer to modules.
    :param callables: Prune variables which refer to callables.
    :param upper: Prune variables with all-uppercase identifiers (underscores
        allowed), which are likely to be intentional global variables (constants
        and the like).
    :param dunder: Prune variables whose name starts with a double underscore.
    :param sunder: Prune variables whose name starts with a single underscore.

    """
    blacklist, whitelist = set(blacklist or ()), set(whitelist or ())
    bw_intersection = blacklist & whitelist
    if bw_intersection:
        raise ValueError(f"Blacklist and whitelist overlap: {bw_intersection}")

    def do_clean_env(globals_to_prune: dict) -> dict:
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
            elif not modules and inspect.ismodule(value):
                remove = False
            elif not callables and callable(value):
                remove = False
            elif not upper and name.isupper():
                remove = False
            elif not dunder and name.startswith("__"):
                remove = False
            elif not sunder and name.startswith("_"):
                remove = False

            if remove:
                pruned_globals[name] = globals_to_prune.pop(name)
            if restore:
                globals_to_prune[name] = builtin

        return pruned_globals

    current_frame = inspect.currentframe()
    if current_frame is None:
        raise RuntimeError("Your Python has no stack frame support in the interpreter")
    user_frame, clean_env_gen = _get_user_frame_and_generator(current_frame)

    # TODO: Maybe try an alternative approach: replace user_frame.f_globals with
    # a dict subclass with a customized getter which will check the position of
    # the current frame in the call stack before allowing access? This could
    # result in both strict and non-strict mode using the same code, which would
    # be good.

    if strict:
        globals_to_prune = user_frame.f_globals
        pruned_globals = do_clean_env(globals_to_prune)
        try:
            yield
        finally:
            globals_to_prune.update(pruned_globals)
    else:

        def global_trace(frame, event, arg):
            # this means we've reached clean_env's matching __exit__ frame in
            # contextlib -> stop tracing
            if getattr(frame.f_locals.get("self"), "gen", None) is clean_env_gen:
                sys.settrace(None)
                return

            globals_to_prune = frame.f_globals
            pruned_globals = do_clean_env(globals_to_prune)
            frame.f_trace_lines = False

            def local_trace(frame, event, arg):
                if event == "return":
                    globals_to_prune.update(pruned_globals)

            return local_trace

        sys.settrace(global_trace)
        yield


# vi: set foldmethod=marker:
