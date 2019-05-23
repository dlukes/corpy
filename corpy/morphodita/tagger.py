from . import log

from collections import namedtuple
from collections.abc import Iterable
from lazy import lazy
from functools import lru_cache
import ufal.morphodita as ufal

Token = namedtuple("Token", "word lemma tag")


class Tagger:
    """A MorphoDiTa morphological tagger and lemmatizer associated with particular
    set of tagging models.

    """

    _NO_TOKENIZER = (
        "No tokenizer defined for tagger {!r}! Please provide "
        "pre-tokenized and sentence-split input."
    )
    _TEXT_REQS = (
        "Please provide a string or an iterable of iterables (not "
        "strings!) of strings as the ``text`` parameter."
    )

    def __init__(self, tagger):
        """Create a ``Tagger`` object.

        :param tagger: Path to the pre-compiled tagging models.
        :type tagger: str

        """
        self._tpath = tagger
        log.info("Loading tagger.")
        self._tagger = ufal.Tagger.load(tagger)
        if self._tagger is None:
            raise RuntimeError("Unable to load tagger from {!r}!".format(tagger))
        self._morpho = self._tagger.getMorpho()
        self._forms = ufal.Forms()
        self._lemmas = ufal.TaggedLemmas()
        self._tokens = ufal.TokenRanges()
        self._tokenizer = self._tagger.newTokenizer()
        if self._tokenizer is None:
            log.warn(self._NO_TOKENIZER.format(tagger))

    @lazy
    def _vtokenizer(self):
        return ufal.Tokenizer_newVerticalTokenizer()

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
        except AttributeError as e:
            converters = [
                a[1:-10]
                for a in dir(self)
                if "converter" in a and a != "_get_converter"
            ]
            raise ValueError(
                "Unknown converter {!r}. Available converters: "
                "{!r}.".format(convert, converters)
            ) from e
        return converter

    def tag(self, text, sents=False, guesser=False, convert=None):
        """Perform morphological tagging and lemmatization on text.

        If ``text`` is a string, sentence-split, tokenize and tag that string.
        If it's an iterable of iterables (typically a list of lists), then take
        each nested iterable as a separate sentence and tag it, honoring the
        provided sentence boundaries and tokenization.

        :param text: Input text.
        :type text: Either str (tokenization is left to the tagger) or iterable
        of iterables (of str), representing individual sentences.
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

        >>> list(t.tag("Je zima. Bude sněžit."))
        [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
         Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
         Token(word='.', lemma='.', tag='Z:-------------')]

        >>> list(t.tag([['Je', 'zima', '.'], ['Bude', 'sněžit', '.']]))
        [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
         Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
         Token(word='.', lemma='.', tag='Z:-------------'),
         Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
         Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
         Token(word='.', lemma='.', tag='Z:-------------')]

        >>> list(t.tag("Je zima. Bude sněžit.", sents=True))
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
        """This is the method ``Tagger.tag()`` delegates to when ``text`` is a
        string. See docstring for ``Tagger.tag()`` for details about parameters.

        """
        converter = self._get_converter(convert)
        if self._tokenizer is None:
            raise RuntimeError(self._NO_TOKENIZER.format(self._tpath))
        yield from self._tag(text, self._tokenizer, sents, guesser, converter)

    def tag_tokenized(self, text, sents=False, guesser=False, convert=None):
        """This is the method ``Tagger.tag()`` delegates to when ``text`` is an
        iterable of iterables of strings. See docstring for ``Tagger.tag()``
        for details about parameters.

        """
        converter = self._get_converter(convert)
        for sent in text:
            # refuse to process if sent is a string or not an iterable, because
            # that would result in tagging each character separately, which is
            # nonsensical
            if isinstance(sent, str) or not isinstance(sent, Iterable):
                raise TypeError(self._TEXT_REQS)
            yield from self._tag(
                "\n".join(sent), self._vtokenizer, sents, guesser, converter
            )

    def _tag(self, text, tokenizer, sents, guesser, converter):
        tagger, forms, lemmas, tokens = (
            self._tagger,
            self._forms,
            self._lemmas,
            self._tokens,
        )
        tokenizer.setText(text)
        while tokenizer.nextSentence(forms, tokens):
            tagger.tag(forms, lemmas, guesser)
            s = []
            for i in range(len(lemmas)):
                lemma = lemmas[i]
                t = tokens[i]
                word = text[t.start : t.start + t.length]  # noqa: E203
                if converter is not None:
                    converter.convert(lemma)
                token = Token(word, lemma.lemma, lemma.tag)
                if sents:
                    s.append(token)
                else:
                    yield token
            if sents:
                yield s
