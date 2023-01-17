"""An interface to MorphoDiTa taggers.

"""
from collections.abc import Iterable, Iterator
from functools import lru_cache
from pathlib import Path
from typing import Literal, NamedTuple, overload
import warnings

import ufal.morphodita as ufal


class Token(NamedTuple):
    word: str
    lemma: str
    tag: str


class Tagger:
    """A MorphoDiTa morphological tagger and lemmatizer.

    :param tagger_path: Path to the pre-compiled tagging models to load.

    """

    _NO_TOKENIZER = (
        "No tokenizer defined for tagger {!r}! Please provide "
        "pre-tokenized and sentence-split input."
    )
    _TEXT_REQS = (
        "Please provide a string or an iterable of iterables (not "
        "strings!) of strings as the ``text`` parameter."
    )

    def __init__(self, tagger_path: Path | str):
        self._tagger_path = tagger_path
        self._tagger = ufal.Tagger.load(str(tagger_path))
        if self._tagger is None:
            raise RuntimeError(f"Unable to load tagger from {tagger_path!r}!")
        self._morpho = self._tagger.getMorpho()
        self._has_tokenizer = self._tagger.newTokenizer() is not None
        if not self._has_tokenizer:
            warnings.warn(self._NO_TOKENIZER.format(tagger_path))

    @lru_cache(maxsize=16)
    def _get_converter(self, convert: str | None) -> ufal.TagsetConverter | None:
        match convert:
            case "pdt_to_conll2009":
                return ufal.TagsetConverter.newPdtToConll2009Converter()
            case "strip_lemma_comment":
                return ufal.TagsetConverter.newStripLemmaCommentConverter(self._morpho)
            case "strip_lemma_id":
                return ufal.TagsetConverter.newStripLemmaIdConverter(self._morpho)
            case None:
                return None
            case _:
                raise ValueError(
                    f"Unknown converter {convert!r}. Available converters: "
                    "pdt_to_conll2009, strip_lemma_comment, strip_lemma_id."
                )

    @overload
    def tag(
        self,
        text: str | Iterable[Iterable[str]],
        *,
        sents: Literal[False] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token]:
        ...

    @overload
    def tag(
        self,
        text: str | Iterable[Iterable[str]],
        *,
        sents: Literal[True] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[list[Token]]:
        ...

    @overload
    def tag(
        self,
        text: str | Iterable[Iterable[str]],
        *,
        sents: bool = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        ...

    def tag(
        self,
        text: str | Iterable[Iterable[str]],
        *,
        sents: bool = False,
        guesser: bool = False,
        convert: str | None = None,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        """Perform morphological tagging and lemmatization on text.

        If ``text`` is a string, sentence-split, tokenize and tag that string.
        If it's an iterable of iterables of strings (typically a list of lists
        of strings), then take each nested iterable as a separate sentence and
        tag it, honoring the provided sentence boundaries and tokenization.

        :param text: Input text:
        :param sents: If ``True``, return an iterator of lists of tokens, each
            list being a sentence, instead of a flat iterator of tokens.
        :param guesser: If ``True``, use the morphological guesser provided with
            the tagger (if available).
        :param convert: Conversion strategy to apply to lemmas and / or tags
            before outputting them. One of ``"pdt_to_conll2009"``,
            ``"strip_lemma_comment"`` or ``"strip_lemma_id"``, or ``None`` if no
            conversion is required.

        >>> tagger = Tagger("./czech-morfflex-pdt.tagger")
        >>> from pprint import pprint
        >>> tokens = list(tagger.tag("Je zima. Bude sněžit."))
        >>> pprint(tokens)
        [Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
         Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
         Token(word='.', lemma='.', tag='Z:-------------')]
        >>> tokens = list(tagger.tag([['Je', 'zima', '.'], ['Bude', 'sněžit', '.']]))
        >>> pprint(tokens)
        [Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
         Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
         Token(word='.', lemma='.', tag='Z:-------------')]
        >>> sents = list(tagger.tag("Je zima. Bude sněžit.", sents=True))
        >>> pprint(sents)
        [[Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
          Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
          Token(word='.', lemma='.', tag='Z:-------------')],
         [Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
          Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
          Token(word='.', lemma='.', tag='Z:-------------')]]

        """
        if isinstance(text, str):
            yield from self.tag_untokenized(
                text, sents=sents, guesser=guesser, convert=convert
            )
        # The other accepted type of input is an iterable of iterables of
        # strings, but we only do a partial check whether the top-level object
        # is an iterable, because e.g. generators would have to be consumed in
        # order to inspect its first item. A second check which signals the
        # frequent mistake of passing an iterable of strings (which results in
        # tagging each character separately) occurs in ``Tagger.tag_tokenized()``.
        elif isinstance(text, Iterable):
            yield from self.tag_tokenized(
                text, sents=sents, guesser=guesser, convert=convert
            )
        else:
            raise TypeError(self._TEXT_REQS)

    @overload
    def tag_untokenized(
        self,
        text: str,
        *,
        sents: Literal[False] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token]:
        ...

    @overload
    def tag_untokenized(
        self,
        text: str,
        *,
        sents: Literal[True] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[list[Token]]:
        ...

    @overload
    def tag_untokenized(
        self,
        text: str,
        *,
        sents: bool = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        ...

    def tag_untokenized(
        self,
        text: str,
        *,
        sents: bool = False,
        guesser: bool = False,
        convert: str | None = None,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        """This is the method :meth:`tag` delegates to when `text` is a string.
        See docstring for :meth:`tag` for details about parameters.

        """
        if not self._has_tokenizer:
            raise RuntimeError(self._NO_TOKENIZER.format(self._tagger_path))
        tokenizer = self._tagger.newTokenizer()
        tokenizer.setText(text)
        converter = self._get_converter(convert)
        forms = ufal.Forms()
        tagged_lemmas = ufal.TaggedLemmas()
        token_ranges = ufal.TokenRanges()
        yield from self._tag(
            tokenizer,
            sents,
            self._morpho.GUESSER if guesser else self._morpho.NO_GUESSER,
            converter,
            forms,
            tagged_lemmas,
            token_ranges,
        )

    @overload
    def tag_tokenized(
        self,
        text: Iterable[Iterable[str]],
        *,
        sents: Literal[False] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token]:
        ...

    @overload
    def tag_tokenized(
        self,
        text: Iterable[Iterable[str]],
        *,
        sents: Literal[True] = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[list[Token]]:
        ...

    @overload
    def tag_tokenized(
        self,
        text: Iterable[Iterable[str]],
        *,
        sents: bool = ...,
        guesser: bool = ...,
        convert: str | None = ...,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        ...

    def tag_tokenized(
        self,
        text: Iterable[Iterable[str]],
        *,
        sents: bool = False,
        guesser: bool = False,
        convert: str | None = None,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        """This is the method :meth:`tag` delegates to when `text` is an
        iterable of iterables of strings. See docstring for :meth:`tag` for
        details about parameters.

        """
        vtokenizer = ufal.Tokenizer.newVerticalTokenizer()
        converter = self._get_converter(convert)
        forms = ufal.Forms()
        tagged_lemmas = ufal.TaggedLemmas()
        token_ranges = ufal.TokenRanges()
        for sent in text:
            # refuse to process if sent is a string (because that would result
            # in tagging each character separately, which is nonsensical), or
            # more generally, not an iterable,
            if isinstance(sent, str) or not isinstance(sent, Iterable):
                raise TypeError(self._TEXT_REQS)
            vtokenizer.setText("\n".join(sent))
            yield from self._tag(
                vtokenizer,
                sents,
                self._morpho.GUESSER if guesser else self._morpho.NO_GUESSER,
                converter,
                forms,
                tagged_lemmas,
                token_ranges,
            )

    @overload
    def _tag(
        self,
        tokenizer: ufal.Tokenizer,
        sents: Literal[False],
        guesser: int,
        converter: ufal.TagsetConverter | None,
        forms: ufal.Forms,
        tagged_lemmas: ufal.TaggedLemmas,
        token_ranges: ufal.TokenRanges,
    ) -> Iterator[Token]:
        ...

    @overload
    def _tag(
        self,
        tokenizer: ufal.Tokenizer,
        sents: Literal[True],
        guesser: int,
        converter: ufal.TagsetConverter | None,
        forms: ufal.Forms,
        tagged_lemmas: ufal.TaggedLemmas,
        token_ranges: ufal.TokenRanges,
    ) -> Iterator[list[Token]]:
        ...

    @overload
    def _tag(
        self,
        tokenizer: ufal.Tokenizer,
        sents: bool,
        guesser: int,
        converter: ufal.TagsetConverter | None,
        forms: ufal.Forms,
        tagged_lemmas: ufal.TaggedLemmas,
        token_ranges: ufal.TokenRanges,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        ...

    def _tag(
        self,
        tokenizer: ufal.Tokenizer,
        sents: bool,
        guesser: int,
        converter: ufal.TagsetConverter | None,
        forms: ufal.Forms,
        tagged_lemmas: ufal.TaggedLemmas,
        token_ranges: ufal.TokenRanges,
    ) -> Iterator[Token] | Iterator[list[Token]]:
        while tokenizer.nextSentence(forms, token_ranges):
            self._tagger.tag(forms, tagged_lemmas, guesser)
            sent = [] if sents else None
            for tagged_lemma, word in zip(tagged_lemmas, forms):
                if converter is not None:
                    converter.convert(tagged_lemma)
                token = Token(word, tagged_lemma.lemma, tagged_lemma.tag)
                if sent is not None:
                    sent.append(token)
                else:
                    yield token
            if sent is not None:
                yield sent
