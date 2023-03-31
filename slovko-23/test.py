from corpy.phonetics import cs


def main():
    with open("../tests/test_phonetics_regressions.tsv", encoding="utf-8") as file:
        for line in file:
            ort, _ = line.rstrip("\n").split("\t")
            cs.transcribe(ort)


if __name__ == "__main__":
    main()
