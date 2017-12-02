def glimpse(obj, max_len=25):
    """Get repr of object, truncated if too long."""
    rep = repr(obj)
    return rep[:20] + "..." + rep[-1] if len(rep) > max_len else rep


def cmp(lhs, rhs, test="__eq__"):
    """Wrap assert statement to automatically raise an informative error."""
    msg = f"{glimpse(lhs)} {test} {glimpse(rhs)} is not True!"
    ans = getattr(lhs, test)(rhs)
    # operators automatically fall back to identity comparison if the
    # comparison is not implemented for the given types, magic methods don't →
    # if comparison is not implemented, we must fall back to identity
    # comparison manually, because NotImplemented is truthy and makes the
    # assert succeed
    if ans is NotImplemented:
        ans = lhs is rhs
    assert ans, msg
