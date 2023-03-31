from corpy.phonetics import cs
from corpy.morphodita import Tagger


def main():
    tagger = Tagger("../czech-morfflex-pdt.tagger")
    with open("../tests/test_phonetics_regressions.tsv", encoding="utf-8") as file:
        for line in file:
            ort, ref_fon = line.rstrip("\n").split("\t")
            ref_fon = tuple(ref_fon.split())
            fon = cs.transcribe(ort, hiatus=True, tagger=tagger, alphabet="CNC")[0]
            assert fon == ref_fon, (fon, ref_fon)


if __name__ == "__main__":
    main()
