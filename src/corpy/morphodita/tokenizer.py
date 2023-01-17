"""An interface to MorphoDiTa tokenizers.

"""
from __future__ import annotations
import collections.abc as c
from pathlib import Path
import typing as t

import ufal.morphodita as ufal


class Tokenizer:
    """A wrapper API around the tokenizers offered by MorphoDiTa.

    :param tokenizer_type: Tokenizer type, see below for possible values.

    ``tokenizer_type`` is typically one of:

    - ``"czech"``: a tokenizer tuned for Czech
    - ``"english"``: a tokenizer tuned for English
    - ``"generic"``: a generic tokenizer
    - ``"vertical"``: a simple tokenizer for the vertical format, which is
      effectively already tokenized (one word per line)

    Specifically, the available tokenizers are determined by the
    ``new_*_tokenizer`` static methods on the MorphoDiTa ``tokenizer`` class
    described in the `MorphoDiTa API reference
    <https://ufal.mff.cuni.cz/morphodita/api-reference#tokenizer>`__.

    """

    def __init__(self, tokenizer_type: str):
        constructor_name = "new" + tokenizer_type.capitalize() + "Tokenizer"
        self.tokenizer_constructor = getattr(ufal.Tokenizer, constructor_name)

    @classmethod
    def from_tagger(cls, tagger_path: str | Path) -> t.Self:
        """Load tokenizer associated with tagger file."""
        self = cls("generic")
        tagger = ufal.Tagger.load(str(tagger_path))
        self.tokenizer_constructor = tagger.newTokenizer
        if self.tokenizer_constructor() is None:
            raise RuntimeError(f"The tagger {tagger_path} has no associated tokenizer.")
        return self

    @t.overload
    def tokenize(self, text: str, sents: t.Literal[False]) -> c.Iterator[str]:
        ...

    @t.overload
    def tokenize(self, text: str, sents: t.Literal[True]) -> c.Iterator[list[str]]:
        ...

    @t.overload
    def tokenize(
        self, text: str, sents: bool = ...
    ) -> c.Iterator[str] | c.Iterator[list[str]]:
        ...

    def tokenize(
        self, text: str, sents: bool = False
    ) -> c.Iterator[str] | c.Iterator[list[str]]:
        """Tokenize `text`.

        :param text: Text to tokenize.
        :param sents: If ``True``, return an iterator of lists of tokens, each
            list being a sentence, instead of a flat iterator of tokens.

        Note that MorphoDiTa performs both sentence splitting and tokenization
        at the same time, but this method iterates over tokens without sentence
        boundaries by default:

        >>> from corpy.morphodita import Tokenizer
        >>> t = Tokenizer("generic")
        >>> for word in t.tokenize("foo bar baz"):
        ...     print(word)
        ...
        foo
        bar
        baz

        If you want to iterate over sentences (lists of tokens), set
        ``sents=True``:

        >>> for sentence in t.tokenize("foo bar baz", sents=True):
        ...     print(sentence)
        ...
        ['foo', 'bar', 'baz']

        """
        # this is more elegant than just segfaulting in the MorphoDiTa C++
        # library if None is passed...
        if not isinstance(text, str):
            raise TypeError(f"``text`` should be str, you passed in {type(text)}.")
        forms = ufal.Forms()
        token_ranges = ufal.TokenRanges()
        tokenizer = self.tokenizer_constructor()
        tokenizer.setText(text)
        while tokenizer.nextSentence(forms, token_ranges):
            if sents:
                yield list(forms)
            else:
                yield from forms
