"""An interface to MorphoDiTa tokenizers.

In addition to tokenization, the MorphoDiTa tokenizers perform sentence
splitting at the same time.

>>> from corpy.morphodita import Tokenizer
>>> t = Tokenizer("generic")
>>> for sentence in t.tokenize("foo bar baz"):
...     print(sentence)
...
['foo', 'bar', 'baz']

Four different tokenizer flavors are available in MorphoDiTa, which you
specify as the first string argument to the ``Tokenizer`` constructor:

- ``vertical``: a simple tokenizer for the vertical format, which is
  effectively already tokenized (one word per line)
- ``czech``: a tokenizer tuned for Czech
- ``english``: a tokenizer tuned for English
- ``generic``: a generic tokenizer

If you want to tokenize multiple texts in parallel, create multiple tokenizer
objects, as each tokenizer can only be tokenizing one text at a time.

"""
import ufal.morphodita as ufal

from .util import generator_with_shared_state


class Tokenizer:
    """A wrapper API around the tokenizers offered by MorphoDiTa.

    >>> t = Tokenizer("generic")
    >>> for sentence in t.tokenize("foo bar baz"):
    ...     print(sentence)
    ...
    ['foo', 'bar', 'baz']

    Available tokenizers (specified by the first parameter to the
    ``Tokenizer()`` constructor): "vertical", "czech", "english",
    "generic". See the ``new*`` static methods on the MorphoDiTa
    ``tokenizer`` class described at
    https://ufal.mff.cuni.cz/morphodita/api-reference#tokenizer for
    details.

    """

    def __init__(self, tokenizer_type):
        """Create a new tokenizer instance.

        :param tokenizer_type: Type of the requested tokenizer, depends on the tokenizer
        constructors made available on the ``tokenizer`` class in MorphoDiTa. Typically one of
        "vertical", "czech", "english" and "generic".
        :type tokenizer_type: str

        """
        constructor = "new" + tokenizer_type.capitalize() + "Tokenizer"
        self._tokenizer = getattr(ufal.Tokenizer, constructor)()
        self._forms = ufal.Forms()
        self._tokens = ufal.TokenRanges()

    @generator_with_shared_state
    def tokenize(self, text):
        """Tokenize ``text``.

        :param text: Text to tokenize.
        :type text: str

        The method returns a generator of sentences as lists of strings. The
        underlying tokenizer is shared by all such generators, so if you try
        to start tokenizing a new text before you've exhausted the generator
        for a previous one, a ``RuntimeError`` will be raised.

        If you want to tokenize in parallel, either create multiple
        tokenizers:

        >>> t1 = Tokenizer("generic")
        >>> t2 = Tokenizer("generic")
        >>> toks1 = t1.tokenize("Foo bar baz. Bar baz qux.")
        >>> toks2 = t2.tokenize("A b c. D e f. G h i.")
        >>> for s1, s2 in zip(toks1, toks2):
        ...     for t1, t2 in zip(s1, s2):
        ...         print(t1, t2)
        Foo A
        bar b
        baz c
        . .
        Bar D
        baz e
        qux f
        . .

        Or exhaust the generators and zip the resulting lists:

        >>> t = Tokenizer("generic")
        >>> toks1 = list(t.tokenize("Foo bar baz. Bar baz qux."))
        >>> toks2 = list(t.tokenize("A b c. D e f. G h i."))
        >>> for s1, s2 in zip(toks1, toks2):
        ...     for t1, t2 in zip(s1, s2):
        ...         print(t1, t2)
        Foo A
        bar b
        baz c
        . .
        Bar D
        baz e
        qux f
        . .

        """
        # this is more elegant than just segfaulting in the MorphoDiTa C++ library if None is
        # passed...
        if not isinstance(text, str):
            raise TypeError(
                "``text`` should be a str, you passed in {}.".format(type(text))
            )
        self._tokenizer.setText(text)
        while self._tokenizer.nextSentence(self._forms, self._tokens):
            yield list(self._forms)
