"""A dummy re module for testing no_globals with strict=True.

"""

_cache = True


def match():
    assert _cache
