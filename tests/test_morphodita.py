import pytest

from corpy.morphodita import Tokenizer, Tagger
from corpy.morphodita.tagger import Token

# ----------------------------- Tokenizer -----------------------------


def test_tokenize_simple():
    tokenizer = Tokenizer("generic")
    words = tokenizer.tokenize("A b. C d.")
    assert next(words) == "A"
    assert next(words) == "b"
    assert next(words) == "."
    assert next(words) == "C"
    assert next(words) == "d"
    assert next(words) == "."
    with pytest.raises(StopIteration):
        next(words)


def test_tokenize_with_sents():
    tokenizer = Tokenizer("generic")
    sents = tokenizer.tokenize("A b. C d.", True)
    assert next(sents) == "A b .".split()
    assert next(sents) == "C d .".split()
    with pytest.raises(StopIteration):
        next(sents)


def test_tokenizer_from_tagger():
    tokenizer = Tokenizer.from_tagger("./czech-morfflex-pdt-161115.tagger")
    tokens = list(tokenizer.tokenize("Kočka leze dírou, pes oknem."))
    assert tokens == "Kočka leze dírou , pes oknem .".split()


def test_tokenize_two_strings_in_parallel_with_same_tokenizer():
    # this didn't use to work; previously, the first generator was truncated
    # after the second started to be yielded from, and even before that,
    # unexpected and incorrect results were generated
    tokenizer = Tokenizer("generic")
    for sent1, sent2 in zip(
        tokenizer.tokenize("a b c", True), tokenizer.tokenize("d e f", True)
    ):
        for tok1, tok2 in zip(sent1, sent2):
            assert ord(tok1) + 3 == ord(tok2)


def test_tokenize_two_strings_intermittently_with_same_tokenizer():
    # ditto
    tokenizer = Tokenizer("generic")
    sents1 = tokenizer.tokenize("A b c. D e f.", True)
    sents2 = tokenizer.tokenize("G h i. J k l.", True)
    assert next(sents1) == "A b c .".split()
    assert next(sents2) == "G h i .".split()
    assert next(sents2) == "J k l .".split()
    assert next(sents1) == "D e f .".split()


# ----------------------------- Tagger -----------------------------


def test_tagger_simple():
    tagger = Tagger("./czech-morfflex-pdt-161115.tagger")
    tokens = list(tagger.tag("Kočka leze dírou, pes oknem."))
    print(tokens)
    assert tokens == [
        Token(word="Kočka", lemma="kočka", tag="NNFS1-----A----"),
        Token(word="leze", lemma="lézt", tag="VB-S---3P-AA---"),
        Token(word="dírou", lemma="díra", tag="NNFS7-----A----"),
        Token(word=",", lemma=",", tag="Z:-------------"),
        Token(word="pes", lemma="pes_^(zvíře)", tag="NNMS1-----A----"),
        Token(word="oknem", lemma="okno", tag="NNNS7-----A----"),
        Token(word=".", lemma=".", tag="Z:-------------"),
    ]


def test_tagger_with_sents():
    tagger = Tagger("./czech-morfflex-pdt-161115.tagger")
    tokens = list(tagger.tag("Kočka leze dírou. Pes oknem.", sents=True))
    print(tokens)
    assert tokens == [
        [
            Token(word="Kočka", lemma="kočka", tag="NNFS1-----A----"),
            Token(word="leze", lemma="lézt", tag="VB-S---3P-AA---"),
            Token(word="dírou", lemma="díra", tag="NNFS7-----A----"),
            Token(word=".", lemma=".", tag="Z:-------------"),
        ],
        [
            Token(word="Pes", lemma="pes_^(zvíře)", tag="NNMS1-----A----"),
            Token(word="oknem", lemma="okno", tag="NNNS7-----A----"),
            Token(word=".", lemma=".", tag="Z:-------------"),
        ],
    ]


def test_tag_two_strings_in_parallel_with_same_tagger():
    # this didn't use to work; previously, the first generator was truncated
    # after the second started to be yielded from, and even before that,
    # unexpected and incorrect results were generated
    tagger = Tagger("./czech-morfflex-pdt-161115.tagger")
    tokens1 = []
    tokens2 = []
    iter1 = tagger.tag("Kočka leze dírou.")
    iter2 = tagger.tag("Pes oknem.")
    for tok1, tok2 in zip(iter1, iter2):
        tokens1.append(tok1.word)
        tokens2.append(tok2.word)
    assert tokens1 == "Kočka leze dírou".split()
    assert tokens2 == "Pes oknem .".split()


def test_tag_two_strings_intermittently_with_same_tagger():
    # ditto
    tagger = Tagger("./czech-morfflex-pdt-161115.tagger")
    iter1 = tagger.tag("Kočka leze dírou.")
    iter2 = tagger.tag("Pes oknem.")
    assert next(iter1).word == "Kočka"
    assert next(iter2).word == "Pes"
    assert next(iter2).word == "oknem"
    assert next(iter1).word == "leze"
