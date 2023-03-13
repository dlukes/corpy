"""A dummy re module for testing clean_env with strict=True.

"""

_cache = True


def match():
    assert _cache
