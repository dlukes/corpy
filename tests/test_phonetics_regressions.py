import pytest
from pathlib import Path

from corpy.phonetics import cs
from corpy.morphodita import Tagger

SCRIPT_DIR = Path(__file__).parent
TAGGER = Tagger(SCRIPT_DIR.parent / "czech-morfflex-pdt-161115.tagger")
CASES = [
    case.split("\t")
    for case in (SCRIPT_DIR / "test_phonetics_regressions.tsv")
    .read_text(encoding="utf-8")
    .splitlines()[1:]
]


@pytest.mark.parametrize("orth,phon_expected", CASES)
def test_regressions(orth, phon_expected):
    """Test all transcriptions that worked at some point."""
    phon = cs.transcribe(orth, alphabet="cnc", hiatus=True, tagger=TAGGER)
    phon = " ".join(phone for word in phon for phone in word)
    assert phon == phon_expected
