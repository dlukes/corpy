import pytest

from corpy.morphodita import Tokenizer
from corpy.morphodita.util import generator_with_shared_state


class TrickyCharSplitter:
    """A class for testing the generator_with_shared_state decorator.

    Using an integer (self.index) as shared state is stupid of course, in
    practice, this will be an object which is necessary for the generator
    to operate, has state, and is possibly expensive to create (e.g. a
    tokenizer).

    """

    def chars(self, string):
        """Yield chars in string one by one."""
        self.index = 0
        while self.index < len(string):
            yield string[self.index]
            self.index += 1


def test_demonstrate_shared_state_generator_problem():
    tcs = TrickyCharSplitter()
    gen1 = tcs.chars("abc")
    gen2 = tcs.chars("def")
    assert next(gen1) == "a"
    assert next(gen2) == "d"
    assert next(gen2) == "e"
    # the following makes sense if you know the implementation details of
    # TrickyCharSplitter (both gen1 and gen2 share the same self.index)
    # but it's unexpected and unfortunate from a user perspective
    assert next(gen1) == "c"  # instead of "b", which would be expected here


class SafeCharSplitter(TrickyCharSplitter):
    @generator_with_shared_state
    def chars(self, string):
        yield from super().chars(string)


def test_demonstrate_how_to_solve_shared_state_generator_problem():
    scs = SafeCharSplitter()
    gen1 = scs.chars("abc")
    gen2 = scs.chars("def")
    assert next(gen1) == "a"
    # unlike with TrickyCharSplitter, this actually works as expected, and the
    # user is warned that the previously created gen has been truncated...
    assert next(gen2) == "d"
    # ... i.e. it will yield no more elements:
    assert list(gen1) == []
    assert list(gen2) == ["e", "f"]


def test_tokenizing_new_text_truncates_previous_one():
    tokenizer = Tokenizer("generic")
    gen1 = tokenizer.tokenize("foo bar baz")
    next(gen1)
    gen2 = tokenizer.tokenize("foo bar baz")
    next(gen2)
    # yielding once from gen2 should truncate gen1
    with pytest.raises(StopIteration):
        next(gen1)
