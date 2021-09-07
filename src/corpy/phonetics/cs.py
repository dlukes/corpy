"""Perform rule-based phonetic transcription of Czech.

Some frequent exceptions to the otherwise fairly regular
orthography-to-phonetics mapping are overridden using a pronunciation
lexicon.

"""
import logging
import warnings
import unicodedata as ud
from functools import lru_cache
from operator import itemgetter
from pathlib import Path
from typing import (
    cast,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import regex as re

from corpy.util import longest_common_substring
from corpy.morphodita import Token, Tagger
from ufal.morphodita import DerivationFormatter  # type: ignore

LOG = logging.getLogger(__name__)


#
# ------------------------------------------------------------------------ Utils {{{1


def _filter_comments(lines):
    for line in lines:
        if not line.strip().startswith("#"):
            yield line


def _load_phones(tsv: str) -> Dict[str, Dict[str, str]]:
    ans: Dict[str, Dict[str, str]] = {}
    lines = tsv.splitlines()
    header_, lines = lines[0], lines[1:]
    header = [h.lower() for h in header_.split("\t")]
    header.pop(0)
    for line_ in _filter_comments(lines):
        line = line_.split("\t")
        key = line.pop(0)
        val = ans.setdefault(key, {})
        for alphabet_id, symbol in zip(header, line):
            val[alphabet_id] = symbol
    return ans


def _load_substr2phones(tsv: str, allowed: Dict) -> Dict[str, List[str]]:
    ans: Dict[str, List[str]] = {}
    lines = tsv.splitlines()
    lines.pop(0)
    for line in _filter_comments(lines):
        substr, phones = line.split("\t")
        phones_for_substr = ans.setdefault(substr, [])
        for phone in phones.split():
            assert phone in allowed, f"Unexpected phone {phone!r}"
            phones_for_substr.append(phone)
    return ans


def _load_voicing_pairs(
    tsv: str, allowed: Dict
) -> Tuple[Dict[str, str], Dict[str, str], Set[str], Set[str]]:
    devoiced2voiced, voiced2devoiced = {}, {}
    lines = tsv.splitlines()
    lines.pop(0)
    for line in _filter_comments(lines):
        devoiced, voiced = line.split("\t")
        assert devoiced in allowed, f"Unexpected phone {devoiced!r}"
        assert voiced in allowed, f"Unexpected phone {voiced!r}"
        devoiced2voiced[devoiced] = voiced
        voiced2devoiced[voiced] = devoiced
    trigger_voicing = set(voiced2devoiced.keys())
    trigger_voicing.remove("v")
    trigger_voicing.remove("P\\")
    trigger_devoicing = set(devoiced2voiced.keys())
    trigger_devoicing.remove("Q\\")
    return devoiced2voiced, voiced2devoiced, trigger_voicing, trigger_devoicing


def _create_substr_re(substr_list: Iterable[str]) -> re.Pattern:
    substr_list = sorted(substr_list, key=len, reverse=True) + ["."]
    return re.compile("|".join(substr_list))


class _ExceptionRewriter:
    def __init__(self, tsv: str):
        lines = tsv.splitlines()
        lines.pop(0)
        rules = []
        for line in _filter_comments(lines):
            match, rewrite = line.split("\t")
            match = f"(?P<x>{match})" if "(" not in match else match
            orig = re.search(r"\(\?P<x>(.*?)\)", match).group(1)
            rules.append((match, orig, rewrite))
        # reverse sort by length of substring matched, so that longest match applies
        rules.sort(key=itemgetter(1), reverse=True)
        re_str = "(" + "|".join(match for (match, _, _) in rules) + ")"
        self._re = re.compile(re_str)
        self._orig2rewrite: Dict[str, str] = {
            orig: rewrite for (_, orig, rewrite) in rules
        }

    @lru_cache()
    def _sub(self, string: str) -> str:
        self._at = 0
        return self._re.sub(self._rewrite, string)

    def _rewrite(self, match) -> str:
        # entire match
        matched = match.group()
        # multiple rewrites are allowed, but they must be contiguous and start
        # at the beginning of the string; otherwise, the match is returned
        # unchanged
        if match.start() == self._at:
            self._at += len(matched)
        else:
            return matched
        # the part of the match we want to replace
        orig = match.group("x")
        # what we want to replace it with
        rewrite = self._orig2rewrite[orig]
        return matched.replace(orig, rewrite)


#
# ------------------------------------------------------------------ Load config {{{1


DIR = Path(__file__)
PHONES = _load_phones(
    DIR.with_name("phones.tsv").read_text(encoding="utf-8")  # pylint: disable=E1101
)
SUBSTR2PHONES = _load_substr2phones(
    DIR.with_name("substr2phones.tsv").read_text(
        encoding="utf-8"
    ),  # pylint: disable=E1101
    PHONES,
)
(
    DEVOICED2VOICED,
    VOICED2DEVOICED,
    TRIGGER_VOICING,
    TRIGGER_DEVOICING,
) = _load_voicing_pairs(
    DIR.with_name("voicing_pairs.tsv").read_text(
        encoding="utf-8"
    ),  # pylint: disable=E1101
    PHONES,
)
SUBSTR_RE = _create_substr_re(SUBSTR2PHONES.keys())
REWRITER = _ExceptionRewriter(
    DIR.with_name("exceptions.tsv").read_text(encoding="utf-8")  # pylint: disable=E1101
)


#
#
# ------------------------------------------------------------------- Public API {{{1


class Phone:
    """A single phone.

    You probably don't need to create these by hand. They're used internally by
    :class:`ProsodicUnit` to keep track of word boundaries while keeping all the
    phones in a flat list.

    """

    def __init__(self, value: str, *, word_boundary: bool = False):
        self.value: str = value
        self.word_boundary = word_boundary

    def __repr__(self):
        return f"/{self.value}/"


EMPTY_PHONE = Phone("")


class ProsodicUnit:
    """A prosodic unit which should be transcribed as a whole.

    This means that various connected speech processes are emulated at word
    boundaries within the unit as well as within words.

    :param orthographic: The orthographic transcript of the prosodic unit.
    :type orthographic: list of str

    """

    def __init__(self, orthographic: List[str]):
        self.orthographic = orthographic
        self._phonetic: Optional[List[Phone]] = None

    def phonetic(
        self,
        *,
        alphabet: str = "SAMPA",
        hiatus=False,
        tagger: Optional[Tagger] = None,
    ) -> List[Tuple[str, ...]]:
        """Phonetic transcription of ProsodicUnit."""
        if self._phonetic is None:
            LOG.debug("Orthographic: %r", self.orthographic)
            trans = self._smart_vowel_seqs(self.orthographic, tagger)
            LOG.debug("Trans after _smart_vowel_seqs: %r", trans)
            trans = self._str2phones(trans)
            LOG.debug("Trans after _str2phones: %r", trans)
            # CSPs are implemented in one reverse pass (assimilation of voicing
            # can propagate) and one forward pass
            trans = self._voicing_assim(trans)
            LOG.debug("Trans after _voicing_assim: %r", trans)
            trans = self._other_csps(trans, hiatus=hiatus)
            LOG.debug("Trans after _other_csps: %r", trans)
            self._phonetic = trans
        return self._split_words_and_translate(self._phonetic, alphabet)

    @staticmethod
    def _smart_vowel_seqs(input_: List[str], tagger: Optional[Tagger]) -> List[str]:
        if tagger is None:
            return input_
        deriv = DerivationFormatter.newPathDerivationFormatter(
            tagger._tagger.getMorpho().getDerivator()
        )
        if deriv.formatDerivation("poukázat").split()[0] == "poukázat":
            warnings.warn(
                "You seem to be using a MorphoDiTa model based on an older version "
                "of DeriNet. Many prefixes won't be detected. Upgrade to a newer "
                "model if possible."
            )

        output = []
        for token in cast(
            Iterator[Token], tagger.tag([input_], convert="strip_lemma_id")
        ):
            word = token.word
            lower = word.lower()
            for lemma in deriv.formatDerivation(token.lemma).split():
                lcs = longest_common_substring(lower, lemma.lower())
                LOG.debug("word: %r, lemma: %r, lcs: %r", word, lemma, lcs)
                if (
                    lcs
                    # we only care about lemmas in the derivation path that
                    # allow us to identify prefixes, i.e. where the common
                    # substring *does not* start at the beginning of the word
                    # form...
                    and (i := lcs.start1) > 0
                    # but it *must* start at the beginning of the lemma
                    # (otherwise word form doutník derived from lemma dutý will
                    # be "morpheme"-split as do-utník because of LCS -ut-, which
                    # is rubbish)
                    and lcs.start2 == 0
                    # currently, we're only aiming to prevent *u diphthongs and
                    # hiatus insertion across morpheme boundaries; in the
                    # future, if we add an option to insert glottal stops, this
                    # will have to be reworked
                    and (lower[i] == "u" or lower[i - 1] in "iíyý")
                ):
                    word = word[:i] + "-" + word[i:]
            output.append(word)
        return output

    @staticmethod
    def _str2phones(input_: List[str]) -> List[Phone]:
        """Convert string to phones.

        Use pronunciation from dictionary if available, fall back to generic
        rewriting rules.

        """
        output: List[Phone] = []
        for word in input_:
            word = word.lower()
            # rewrite exceptions
            word = REWRITER._sub(word)
            # force hiatus in <i[ií]> sequences; <y> is there because the
            # exceptions above can insert it in place of <i> to prevent
            # palatalization
            word = re.sub(r"([iy])([ií])", r"\1j\2", word)
            # remove duplicate graphemes (except for short vowels, cf. <pootevřít>)
            # cf. no gemination below for the phonetic counterpart of this rule
            word = re.sub(r"([^aeoiuy])\1", r"\1", word)
            for match in SUBSTR_RE.finditer(word.lower()):
                substr = match.group()
                try:
                    phones = SUBSTR2PHONES[substr]
                except KeyError as err:
                    raise ValueError(
                        f"Unexpected substring in input: {substr!r}"
                    ) from err
                output.extend(Phone(ph) for ph in phones)
            output[-1].word_boundary = True
        return output

    @staticmethod
    def _voicing_assim(input_: List[Phone]) -> List[Phone]:
        r"""Perform assimilation of voicing.

        Usually regressive, but P\ assimilates progressively as well.

        """
        output = []
        previous_phone = EMPTY_PHONE
        for phone in reversed(input_):
            if previous_phone.value in TRIGGER_VOICING:
                phone.value = DEVOICED2VOICED.get(phone.value, phone.value)
            elif phone.word_boundary or previous_phone.value in TRIGGER_DEVOICING:
                phone.value = VOICED2DEVOICED.get(phone.value, phone.value)
            # for P\, the assimilation works the other way round too
            elif previous_phone.value == "P\\" and phone.value in TRIGGER_DEVOICING:
                previous_phone.value = "Q\\"
            output.append(phone)
            previous_phone = phone
        output.reverse()
        return output

    @staticmethod
    def _other_csps(input_: List[Phone], *, hiatus=False) -> List[Phone]:
        """Perform other connected speech processes."""
        output = []
        for i, phone in enumerate(input_):
            try:
                next_ph = input_[i + 1]
            except IndexError:
                next_ph = EMPTY_PHONE
            # assimilation of place for nasals
            if phone.value == "n" and next_ph.value in ("k", "g"):
                phone.value = "N"
            elif phone.value == "m" and next_ph.value in ("f", "v"):
                phone.value = "F"
            # no gemination (except across word boundaries and for short
            # vowels); cf. remove duplicate graphemes above for the
            # orthographic counterpart of this rule
            elif (
                phone.value == next_ph.value
                and phone.value not in "aEIou"
                and not phone.word_boundary
            ):
                continue
            # drop CSP-blocking pseudophones (they've done their job by now)
            elif phone.value == "-":
                continue
            output.append(phone)
            # optionally add transient /j/ between high front vowel and subsequent vowel
            if (
                hiatus
                and re.match("[Ii]", phone.value)
                and re.match("[aEIoui]", next_ph.value)
            ):
                output.append(Phone("j"))
        return output

    @staticmethod
    def _split_words_and_translate(
        input_: List[Phone], alphabet
    ) -> List[Tuple[str, ...]]:
        output = []
        word = []
        alphabet = alphabet.lower()
        for phone in input_:
            word.append(PHONES.get(phone.value, {}).get(alphabet, phone.value))
            if phone.word_boundary:
                output.append(tuple(word))
                word = []
        return output


def _separate_tokens(
    tokens: List[str], prosodic_boundary_symbols: Set[str]
) -> Tuple[List[Optional[str]], List[str]]:
    """Separate tokens for transcription from those that will be left as is.

    Returns two lists: the first one is a matrix for the result containing
    non-alphabetic tokens and gaps for the alphabetic ones, the second one
    contains just the alphabetic ones.

    """
    matrix: List[Optional[str]] = []
    to_transcribe = []
    for token in tokens:
        if re.fullmatch(r"[\p{Alphabetic}\-]*\p{Alphabetic}[\p{Alphabetic}\-]*", token):
            # instead of simply checking for a final hyphen in the outer
            # condition and silently shoving an otherwise transcribable token
            # into matrix, it's better to fail and alert the user they probably
            # meant something else
            if token.endswith("-"):
                raise ValueError(
                    f"Can't transcribe token ending with hyphen ({token!r}), place hyphen at "
                    "beginning of next token instead"
                )
            to_transcribe.append(token)
            matrix.append(None)
        elif token in prosodic_boundary_symbols:
            to_transcribe.append("-")
            matrix.append(token)
        else:
            matrix.append(token)
    return matrix, to_transcribe


def transcribe(
    phrase: Union[str, Iterable[str]],
    *,
    alphabet="sampa",
    hiatus=False,
    tagger: Optional[Tagger] = None,
    # TODO: toggle for glottal stop at boundaries inserted by tagger? in that
    # case, the glottal stop should also trigger devoicing, e.g. podobojí vs.
    # pot?obojí
    prosodic_boundary_symbols: Optional[Set[str]] = None,
) -> List[Union[str, Tuple[str, ...]]]:
    """Phonetically transcribe `phrase`.

    .. note::

       It is **highly recommended** to provide an instance of
       :class:`corpy.morphodita.Tagger` via the `tagger` argument. This enables
       smarter treatment of vowel sequences emerging as a result of prefixing.
       Without a tagger, both e.g. *neuron* and *neurozený* will have *-eu-*
       transcribed as a diphthong, even though it's only appropriate in the
       first case.

       A few simple cases are covered even in the absence of a tagger via the
       exceptions mechanism: search for ``-`` in `exceptions.tsv`_.

    .. _exceptions.tsv: https://github.com/dlukes/corpy/blob/master/src/corpy/phonetics/exceptions.tsv

    `phrase` is either a string (in which case it is split on whitespace) or an
    iterable of strings (in which case it's considered as already tokenized by
    the user).

    Transcription is attempted for tokens which consist purely of alphabetical
    characters and possibly hyphens (``-``). Other tokens are passed through
    unchanged. Hyphens have a special role: they prevent interactions between
    graphemes or phones from taking place, which means you can e.g. cancel
    assimilation of voicing in a cluster like ``tb`` by inserting a hyphen
    between the graphemes: ``t-b``. They are removed from the final output. If
    you want a **literal hyphen**, it must be inside a token with either no
    alphabetic characters, or at least one other non-alphabetic character (e.g.
    ``-``, ``---``, ``-hlad?``, etc.).

    Returns a list where **transcribed tokens** are represented as **tuples of
    strings** (phones) and **non-transcribed tokens** (which were just passed
    through as-is) as plain **strings**.

    `alphabet` is one of SAMPA, IPA, CS or CNC (case insensitive) and determines
    the symbol alphabet used in the phonetic transcript.

    When ``hiatus=True``, a /j/ phone is added between a high front vowel
    and a subsequent vowel.

    Various connected speech processes such as assimilation of voicing are
    emulated even across word boundaries. By default, this happens
    **irrespective of intervening non-transcribed tokens**. If you want some
    types of non-transcribed tokens to constitute an obstacle to interactions
    between phones, pass them as a set via the `prosodic_boundary_symbols`
    argument. E.g. ``prosodic_boundary_symbols={"?", ".."}`` will prevent CSPs
    from being emulated across ``?`` and ``..`` tokens.

    """
    try:
        if isinstance(phrase, str):
            tokens = ud.normalize("NFC", phrase.strip()).split()
        else:
            tokens = [ud.normalize("NFC", t) for t in phrase]
    except TypeError as err:
        raise TypeError(
            f"Expected str or Iterable[str] as phrase argument, got {type(phrase)} instead"
        ) from err
    if prosodic_boundary_symbols is None:
        prosodic_boundary_symbols = set()
    matrix, to_transcribe = _separate_tokens(tokens, prosodic_boundary_symbols)
    transcribed = ProsodicUnit(to_transcribe).phonetic(
        alphabet=alphabet, hiatus=hiatus, tagger=tagger
    )
    return [m if m is not None else transcribed.pop(0) for m in matrix]  # type: ignore


# vi: set foldmethod=marker:
