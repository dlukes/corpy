"""An interface to MorphoDiTa tokenizers.

In addition to tokenization, the MorphoDiTa tokenizers perform sentence splitting at the same time.

The easiest way to get started is to import one of the following pre-instantiated tokenizers:
``vertical``, ``czech``, ``english`` or ``generic``, and use it like so:

>>> from corpy.morphodita.tokenizer import generic
>>> for sentence in generic.tokenize("foo bar baz"):
...     print(sentence)
...
['foo', 'bar', 'baz']

If you want more flexibility, e.g. for tokenizing several in texts in parallel with the same type of
tokenizer, then create your own objects (each tokenizer can only be tokenizing one text at a time!):

>>> from corpy.morphodita.tokenizer import Tokenizer
>>> my_tokenizer1 = Tokenizer("generic")
>>> my_tokenizer2 = Tokenizer("generic")

"""
import ufal.morphodita as ufal


class Tokenizer:
    """A wrapper API around the tokenizers offered by MorphoDiTa.

    Usage:

    >>> t = Tokenizer("generic")
    >>> for sentence in t.tokenize("foo bar baz"):
    ...     print(sentence)
    ...
    ['foo', 'bar', 'baz']

    Available tokenizers (specified by the first parameter to the ``Tokenizer()`` constructor):
    "vertical", "czech", "english", "generic". See the ``new*`` static methods on the MorphoDiTa
    ``tokenizer`` class described at https://ufal.mff.cuni.cz/morphodita/api-reference#tokenizer for
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

    def tokenize(self, text):
        """Tokenize ``text``.

        :param text: Text to tokenize.
        :type text: str

        The method returns a generator of sentences as lists of strings. The underlying tokenizer
        object is shared by all such generators, which means this probably doesn't do what you want
        it to:

        >>> t = Tokenizer("generic")
        >>> toks1 = t.tokenize("Foo bar baz. Bar baz qux.")
        >>> toks2 = t.tokenize("A b c. D e f. G h i.")
        >>> for s1, s2 in zip(toks1, toks2):
        ...     for t1, t2 in zip(s1, s2):
        ...         print(t1, t2)
        Foo A
        bar b
        baz c
        . .
        D G
        e h
        f i
        . .

        What happens in the ``zip()`` call is that the underlying tokenizer's text is first set to
        ``"Foo bar baz. Bar baz qux."``, and the sentence ``['Foo', 'bar', 'baz', '.']`` is yielded
        by ``toks1``. Then it is set to ``"A b c. D e f."`` and ``['A', 'b', 'c', '.']`` is yielded
        by ``toks2``. These two values are zipped and bound to ``(s1, s2)`` in the first iteration
        of the outer for-loop. From this point on, the text doesn't change anymore (we're in the
        loop yielding individual sentences), so **toks1** (now using the same text as ``toks2``)
        yields ``['D', 'e', 'f', '.']`` and **toks2** the last ``['G', 'h', 'i', '.']``. These
        become ``(s1, s2)`` in the second and final iteration of the for-loop, because after this,
        both ``toks1`` and ``toks2`` (since they ended up with the same text) are exhausted.

        For the use case above, either create multiple tokenizers:

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


vertical = Tokenizer("vertical")
czech = Tokenizer("czech")
english = Tokenizer("english")
generic = Tokenizer("generic")
