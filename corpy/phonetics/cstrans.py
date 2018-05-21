from pathlib import Path
from typing import Dict, List, Set, Tuple, Iterable

import regex as re


# ------------------------------ Utils ------------------------------


def _load_phones(tsv: str) -> Dict[str, Dict[str, str]]:
    ans: Dict[str, Dict[str, str]] = {}
    lines = tsv.splitlines()
    header_, lines = lines[0], lines[1:]
    header = [h.lower() for h in header_.split("\t")]
    header.pop(0)
    for line_ in lines:
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
    for line in lines:
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
    for line in lines:
        devoiced, voiced = line.split("\t")
        assert devoiced in allowed, f"Unexpected phone {devoiced!r}"
        assert voiced in allowed, f"Unexpected phone {voiced!r}"
        devoiced2voiced[devoiced] = voiced
        voiced2devoiced[voiced] = devoiced
    trigger_voicing = set(voiced2devoiced.keys())
    trigger_voicing.remove("v")
    trigger_devoicing = set(devoiced2voiced.keys())
    return devoiced2voiced, voiced2devoiced, trigger_voicing, trigger_devoicing


def _create_substr_re(substr_list: Iterable[str]) -> re.Regex:
    substr_list = sorted(substr_list, key=len, reverse=True) + ["."]
    return re.compile("|".join(substr_list))


# ------------------------------ Global variables ------------------------------


DIR = Path(__file__)
PHONES = _load_phones(DIR.with_name("phones.tsv").read_text())
SUBSTR2PHONES = _load_substr2phones(
    DIR.with_name("substr2phones.tsv").read_text(), PHONES)
DEVOICED2VOICED, VOICED2DEVOICED, TRIGGER_VOICING, TRIGGER_DEVOICING = _load_voicing_pairs(
    DIR.with_name("voicing_pairs.tsv").read_text(), PHONES)

SUBSTR_RE = _create_substr_re(SUBSTR2PHONES.keys())


# ------------------------------ Public API ------------------------------


class Phone:

    def __init__(self, value: str, word_boundary: bool = False) -> None:
        self.value = value
        self.word_boundary = word_boundary
        # if False, then this phone can be affected by pronunciation rules
        self.final = False


class ProsodicUnit:
    """A prosodic unit which should be transcribed as a whole.

    This means that various connected speech processes are emulated at word boundaries within the
    unit.

    """

    def __init__(self, input_=List[str]):
        self.input = input_

    def transcribe(self, alphabet: str = "SAMPA") -> List[Tuple[str, ...]]:
        """Perform transcription."""
        t = self._str2phone(self.input)
        t = self._voicing_assim(t)
        # TODO: heuristic
        # TODO: hiatus
        return self._split_words_and_translate(t, alphabet)

    @staticmethod
    def _str2phone(input_: List[str]) -> List[Phone]:
        """Convert string to phones.

        Use pronunciation from dictionary if available, fall back to generic rewriting rules.

        """
        output: List[Phone] = []
        for word in input_:
            # TODO: try to substitute dict-based transcription
            for match in SUBSTR_RE.finditer(word.lower()):
                substr = match.group()
                phones = SUBSTR2PHONES[substr]
                output.extend(Phone(ph) for ph in phones)
            output[-1].word_boundary = True
        return output

    @staticmethod
    def _voicing_assim(input_: List[Phone]) -> List[Phone]:
        """Perform regressive assimilation of voicing."""
        output = []
        previous_phone = Phone("")
        for ph in reversed(input_):
            if not ph.final:
                if previous_phone.value in TRIGGER_VOICING:
                    ph = Phone(
                        DEVOICED2VOICED.get(ph.value, ph.value),
                        ph.word_boundary)
                elif ph.word_boundary or previous_phone.value in TRIGGER_DEVOICING:
                    ph = Phone(
                        VOICED2DEVOICED.get(ph.value, ph.value),
                        ph.word_boundary)
            output.append(ph)
            previous_phone = ph
        output.reverse()
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


def transcribe(phrase: str, alphabet="sampa") -> List[Tuple[str, ...]]:
    """Split ``phrase`` on whitespace and return transcription.

    ``alphabet`` is one of SAMPA, IPA, CS or CNC (case insensitive).

    """
    return ProsodicUnit(phrase.strip().split()).transcribe(alphabet)


s = transcribe("máš hlad")
i = transcribe("máš hlad", "IPA")
c = transcribe("máš hlad", "CS")
k = transcribe("máš hlad", "CNC")
