from pathlib import Path

from corpy.phonetics import cs

DIR = Path(__file__).parent


def test_regressions():
    """Test all transcriptions that worked at some point."""
    fpath = DIR.joinpath("test_phonetics_regressions.tsv")
    cases = fpath.read_text(encoding="utf-8").splitlines()[1:]  # pylint: disable=E1101
    for i, case in enumerate(cases):
        orth, phon = case.split("\t")
        auto = cs.transcribe(orth, alphabet="cnc", hiatus=True)
        auto = " ".join(phone for word in auto for phone in word)
        assert auto == phon, f"auto == phon failed at {fpath}:{i+2}"
