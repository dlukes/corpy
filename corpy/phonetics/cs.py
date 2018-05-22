"""Perform rule-based phonetic transcription of Czech.

Some frequent exceptions to the otherwise fairly regular
orthography-to-phonetics mapping are overridden using a pronunciation
lexicon.

"""
import unicodedata as ud
from functools import lru_cache
from operator import itemgetter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple  # noqa: F401

import regex as re

# ------------------------------ Utils ------------------------------


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
        for k, v in zip(header, line):
            val[k] = v
    return ans


def _load_substr2phones(tsv: str, allowed: Dict) -> Dict[str, List[str]]:
    ans: Dict[str, List[str]] = {}
    lines = tsv.splitlines()
    lines.pop(0)
    for line in _filter_comments(lines):
        substr, phones = line.split("\t")
        phones_for_substr = ans.setdefault(substr, [])
        for ph in phones.split():
            assert ph in allowed, f"Unexpected phone {ph!r}"
            phones_for_substr.append(ph)
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


def _create_substr_re(substr_list: Iterable[str]) -> re.Regex:
    substr_list = sorted(substr_list, key=len, reverse=True) + ["."]
    return re.compile("|".join(substr_list))


class _ExceptionRewriter:

    def __init__(self, tsv: str) -> None:
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
        self._orig2rewrite: Dict[str, str] = {orig: rewrite for (_, orig, rewrite) in rules}

    @lru_cache()
    def sub(self, string: str) -> str:
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


# ------------------------------ Load config ------------------------------


DIR = Path(__file__)
PHONES = _load_phones(DIR.with_name("phones.tsv").read_text())  # pylint: disable=E1101
SUBSTR2PHONES = _load_substr2phones(
    DIR.with_name("substr2phones.tsv").read_text(), PHONES)  # pylint: disable=E1101
DEVOICED2VOICED, VOICED2DEVOICED, TRIGGER_VOICING, TRIGGER_DEVOICING = _load_voicing_pairs(
    DIR.with_name("voicing_pairs.tsv").read_text(), PHONES)  # pylint: disable=E1101

SUBSTR_RE = _create_substr_re(SUBSTR2PHONES.keys())
REWRITER = _ExceptionRewriter(DIR.with_name("exceptions.tsv").read_text())  # pylint: disable=E1101


# ------------------------------ Public API ------------------------------


class Phone:

    def __init__(self, value: str, *, word_boundary: bool = False) -> None:
        self.value: str = value
        self.word_boundary = word_boundary

    def __repr__(self):
        return f"/{self.value}/"


EMPTY_PHONE = Phone("")


class ProsodicUnit:
    """A prosodic unit which should be transcribed as a whole.

    This means that various connected speech processes are emulated at word
    boundaries within the unit as well as within words.

    """

    def __init__(self, orthographic: List[str]) -> None:
        """Initialize ProsodicUnit with orthographic transcript."""
        self.orthographic = orthographic
        self._phonetic: Optional[List[Phone]] = None

    def phonetic(self, alphabet: str = "SAMPA", *, hiatus=False) -> List[Tuple[str, ...]]:
        """Phonetic transcription of ProsodicUnit."""
        if self._phonetic is None:
            t = self._str2phones(self.orthographic)
            # CSPs are implemented in one reverse pass (assimilation of voicing
            # can propagate) and one forward pass
            t = self._voicing_assim(t)
            t = self._other_csps(t, hiatus=hiatus)
            self._phonetic = t
        return self._split_words_and_translate(self._phonetic, alphabet)

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
            word = REWRITER.sub(word)
            # force hiatus in <i[ií]> sequences; <y> is there because the
            # exceptions above can insert it in place of <i> to prevent
            # palatalization
            word = re.sub(r"([iy])([ií])", r"\1j\2", word)
            # remove duplicate graphemes (except for short vowels, cf. <pootevřít>)
            # cf. no gemination below for the phonetic counterpart of this rule
            word = re.sub(r"([^aeoiuy])\1", r"\1", word)
            for match in SUBSTR_RE.finditer(word.lower()):
                substr = match.group()
                phones = SUBSTR2PHONES[substr]
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
        for ph in reversed(input_):
            if previous_phone.value in TRIGGER_VOICING:
                ph.value = DEVOICED2VOICED.get(ph.value, ph.value)
            elif ph.word_boundary or previous_phone.value in TRIGGER_DEVOICING:
                ph.value = VOICED2DEVOICED.get(ph.value, ph.value)
            # for P\, the assimilation works the other way round too
            elif previous_phone.value == "P\\" and ph.value in TRIGGER_DEVOICING:
                previous_phone.value = "Q\\"
            output.append(ph)
            previous_phone = ph
        output.reverse()
        return output

    @staticmethod
    def _other_csps(input_: List[Phone], *, hiatus=False) -> List[Phone]:
        """Perform other connected speech processes."""
        output = []
        for i, ph in enumerate(input_):
            try:
                next_ph = input_[i+1]
            except IndexError:
                next_ph = EMPTY_PHONE
            # assimilation of place for nasals
            if ph.value == "n" and next_ph.value in ("k", "g"):
                ph.value = "N"
            elif ph.value == "m" and next_ph.value in ("f", "v"):
                ph.value = "F"
            # no gemination (except for short vowels)
            # cf. remove duplicate graphemes above for the orthographic counterpart of this rule
            elif ph.value == next_ph.value and ph.value not in "aEIou":
                continue
            # drop CSP-blocking pseudophones (they've done their job by now)
            elif ph.value == "-":
                continue
            output.append(ph)
            # optionally add transient /j/ between high front vowel and subsequent vowel
            if hiatus and re.match("[Ii]", ph.value) and re.match("[aEIoui]", next_ph.value):
                output.append(Phone("j"))
        return output

    @staticmethod
    def _split_words_and_translate(input_: List[Phone], alphabet) -> List[Tuple[str, ...]]:
        output = []
        word = []
        alphabet = alphabet.lower()
        for ph in input_:
            word.append(PHONES.get(ph.value, {}).get(alphabet, ph.value))
            if ph.word_boundary:
                output.append(tuple(word))
                word = []
        return output


def transcribe(phrase: str, *, alphabet="sampa", hiatus=False) -> List[Tuple[str, ...]]:
    """Split ``phrase`` on whitespace and return transcription.

    ``alphabet`` is one of SAMPA, IPA, CS or CNC (case insensitive).

    When ``hiatus == True``, a /j/ phone is added between a high front vowel
    and a subsequent vowel.

    """
    word_list = ud.normalize("NFC", phrase.strip()).split()
    return ProsodicUnit(word_list).phonetic(alphabet, hiatus=hiatus)