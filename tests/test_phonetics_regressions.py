from pathlib import Path

from corpy.phonetics import cstrans as cs

DIR = Path(__file__).parent


def test_regressions():
    """Test all transcriptions that worked at some point."""
    fpath = DIR.joinpath("test_phonetics_regressions.tsv")
    cases = fpath.read_text().splitlines()[1:]  # pylint: disable=E1101
    for i, case in enumerate(cases):
        orth, alphabet, phon = case.split("\t")
        auto = cs.transcribe(orth, alphabet=alphabet, hiatus=True)
        auto = " ".join(phone for word in auto for phone in word)
        assert auto == phon, f"auto == phon failed on l. {i+2} of {fpath}"
