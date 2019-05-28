"""An interface to MorphoDiTa taggers.

"""
from collections import namedtuple
from collections.abc import Iterable
from lazy import lazy
from functools import lru_cache

import ufal.morphodita as ufal

from . import LOG

Token = namedtuple("Token", "word lemma tag")


class Tagger:
    """A MorphoDiTa morphological tagger and lemmatizer.

    :param tagger_path: Path to the pre-compiled tagging models to load.
    :type tagger_path: str

    """

    _NO_TOKENIZER = (
        "No tokenizer defined for tagger {!r}! Please provide "
        "pre-tokenized and sentence-split input."
    )
    _TEXT_REQS = (
        "Please provide a string or an iterable of iterables (not "
        "strings!) of strings as the ``text`` parameter."
    )

    def __init__(self, tagger_path):
        self._tagger_path = tagger_path
        LOG.info("Loading tagger.")
        self._tagger = ufal.Tagger.load(tagger_path)
        if self._tagger is None:
            raise RuntimeError(f"Unable to load tagger from {tagger_path!r}!")
        self._morpho = self._tagger.getMorpho()
        self._has_tokenizer = self._tagger.newTokenizer() is not None
        if not self._has_tokenizer:
            LOG.warning(self._NO_TOKENIZER.format(tagger_path))

    @lazy
    def _pdt_to_conll2009_converter(self):
        return ufal.TagsetConverter_newPdtToConll2009Converter()

    @lazy
    def _strip_lemma_comment_converter(self):
        return ufal.TagsetConverter_newStripLemmaCommentConverter(self._morpho)

    @lazy
    def _strip_lemma_id_converter(self):
        return ufal.TagsetConverter_newStripLemmaIdConverter(self._morpho)

    @lru_cache(maxsize=16)
    def _get_converter(self, convert):
        try:
            converter = (
                getattr(self, "_" + convert + "_converter")
                if convert is not None
                else None
            )
        except AttributeError as err:
            converters = [
                a[1:-10]
                for a in dir(self)
                if "converter" in a and a != "_get_converter"
            ]
            raise ValueError(
                "Unknown converter {!r}. Available converters: "
                "{!r}.".format(convert, converters)
            ) from err
        return converter

    def tag(self, text, *, sents=False, guesser=False, convert=None):
        """Perform morphological tagging and lemmatization on text.

        If ``text`` is a string, sentence-split, tokenize and tag that
        string. If it's an iterable of iterables (typically a list of lists),
        then take each nested iterable as a separate sentence and tag it,
        honoring the provided sentence boundaries and tokenization.

        :param text: Input text.
        :type text: either str (tokenization is left to the tagger) or iterable
            of iterables (of str), representing individual sentences
        :param sents: Whether to signal sentence boundaries by outputting a
            sequence of lists (sentences).
        :type sents: bool
        :param guesser: Whether to use the morphological guesser provided with
            the tagger (if available).
        :type guesser: bool
        :param convert: Conversion strategy to apply to lemmas and / or tags
            before outputting them.
        :type convert: str, one of "pdt_to_conll2009", "strip_lemma_comment" or
            "strip_lemma_id", or None if no conversion is required
        :return: An iterator over the tagged text, possibly grouped into
            sentences if ``sents=True``.

        >>> tagger = Tagger("./czech-morfflex-pdt-161115.tagger")
        >>> from pprint import pprint
        >>> tokens = list(tagger.tag("Je zima. Bude sněžit."))
        >>> pprint(tokens)
        [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
         Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
         Token(word='.', lemma='.', tag='Z:-------------')]
        >>> tokens = list(tagger.tag([['Je', 'zima', '.'], ['Bude', 'sněžit', '.']]))
        >>> pprint(tokens)
        [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
         Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
         Token(word='.', lemma='.', tag='Z:-------------')]
        >>> sents = list(tagger.tag("Je zima. Bude sněžit.", sents=True))
        >>> pprint(sents)
        [[Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
          Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
          Token(word='.', lemma='.', tag='Z:-------------')],
         [Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
          Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
          Token(word='.', lemma='.', tag='Z:-------------')]]

        """
        if isinstance(text, str):
            yield from self.tag_untokenized(text, sents, guesser, convert)
        # The other accepted type of input is an iterable of iterables of
        # strings, but we only do a partial check whether the top-level object
        # is an Iterable, because it would have to be consumed in order to
        # inspect its first item. A second check which signals the frequent
        # mistake of passing an iterable of strings (which results in tagging
        # each character separately) occurs in ``Tagger.tag_tokenized()``.
        elif isinstance(text, Iterable):
            yield from self.tag_tokenized(text, sents, guesser, convert)
        else:
            raise TypeError(self._TEXT_REQS)

    def tag_untokenized(self, text, sents=False, guesser=False, convert=None):
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
            tokenizer, sents, guesser, converter, forms, tagged_lemmas, token_ranges
        )

    def tag_tokenized(self, text, sents=False, guesser=False, convert=None):
        """This is the method :meth:`tag` delegates to when `text` is an
        iterable of iterables of strings. See docstring for :meth:`tag` for
        details about parameters.

        """
        vtokenizer = ufal.Tokenizer_newVerticalTokenizer()
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
                guesser,
                converter,
                forms,
                tagged_lemmas,
                token_ranges,
            )

    def _tag(
        self, tokenizer, sents, guesser, converter, forms, tagged_lemmas, token_ranges
    ):
        while tokenizer.nextSentence(forms, token_ranges):
            self._tagger.tag(forms, tagged_lemmas, guesser)
            if sents:
                sent = []
            for tagged_lemma, word in zip(tagged_lemmas, forms):
                if converter is not None:
                    converter.convert(tagged_lemma)
                token = Token(word, tagged_lemma.lemma, tagged_lemma.tag)
                if sents:
                    sent.append(token)
                else:
                    yield token
            if sents:
                yield sent
