from corpy.phonetics import cstrans as cs


def test_voicing_assimilation_over_word_boundaries():
    assert cs.transcribe("máš hlad") == [("m", "a:", "Z"), ("h\\", "l", "a", "t")]


def test_voicing_assimilation_of_ř():
    assert cs.transcribe("pařát") == [("p", "a", "P\\", "a:", "t")]
    assert cs.transcribe("přát") == [("p", "Q\\", "a:", "t")]
    assert cs.transcribe("hřát") == [("h\\", "P\\", "a:", "t")]


def test_different_output_alphabets():
    assert cs.transcribe("máš hlad", alphabet="IPA") == [("m", "aː", "ʒ"), ("ɦ", "l", "a", "t")]
    assert cs.transcribe("máš hlad", alphabet="CS") == [("m", "á", "ž"), ("h", "l", "a", "t")]
    assert cs.transcribe("máš hlad", alphabet="CNC") == [("m", "á", "ž"), ("h", "l", "a", "t")]


def test_hiatus():
    # no hiatus by default
    assert cs.transcribe("hiát") == [("h\\", "I", "a:", "t")]
    # but can be requested optionally
    assert cs.transcribe("hiát", hiatus=True) == [("h\\", "I", "j", "a:", "t")]


def test_other_csps():
    assert cs.transcribe("tramvaj") == [("t", "r", "a", "F", "v", "a", "j")]
    assert cs.transcribe("kongo") == [("k", "o", "N", "g", "o")]


def test_remove_duplicate_graphemes():
    assert cs.transcribe("denně") == [("d", "E", "J", "E")]
    # short vowels are exempt for obvious reasons:
    assert cs.transcribe("pootevřít") == [("p", "o", "o", "t", "E", "v", "P\\", "i:", "t")]
    assert cs.transcribe("neexistoval") == \
        [("n", "E", "E", "g", "z", "I", "s", "t", "o", "v", "a", "l")]
    assert cs.transcribe("muzeem") == [("m", "u", "z", "E", "E", "m")]
    # but long vowels are not
    assert cs.transcribe("áá") == [("a:",)]


def test_no_gemination():
    assert cs.transcribe("dražší") == [("d", "r", "a", "S", "i:")]


def test_exceptions():
    """NOTE: Use these tests as a source of inspiration as to what can be
    achieved using exceptions. The system is kind of ugly and hacky but
    thanks to that, it's also flexible.

    """
    # partial replacements work as expected...
    assert cs.transcribe("cyklistický") == \
        [('t_s', 'I', 'k', 'l', 'I', 's', 't', 'I', 't_s', 'k', 'i:')]
    assert cs.transcribe("cyklisti") == [('t_s', 'I', 'k', 'l', 'I', 's', 'c', 'I')]
    # ... even with a prefix
    assert cs.transcribe("necyklistický") == \
        [("n", "E", 't_s', 'I', 'k', 'l', 'I', 's', 't', 'I', 't_s', 'k', 'i:')]
    assert cs.transcribe("necyklisti") == [("n", "E", 't_s', 'I', 'k', 'l', 'I', 's', 'c', 'I')]
    # the regex is properly constructed so that longer matches win: this should
    # match komuni...
    assert cs.transcribe("komunita") == [('k', 'o', 'm', 'u', 'n', 'I', 't', 'a')]
    # ... this too...
    assert cs.transcribe("komunisti") == [('k', 'o', 'm', 'u', 'n', 'I', 's', 'c', 'I')]
    # .. and this should match komunisti.
    assert cs.transcribe("komunistický") == \
        [('k', 'o', 'm', 'u', 'n', 'I', 's', 't', 'I', 't_s', 'k', 'i:')]
    # contiguous matches starting at the beginning of the string can be
    # rewritten...
    assert cs.transcribe("antikomunista") == \
        [('a', 'n', 't', 'I', 'k', 'o', 'm', 'u', 'n', 'I', 's', 't', 'a')]
    # ... but once the contiguity is broken (as here by the substring FOO),
    # rewriting stops (notice -JIsta below instead of -nIsta)
    assert cs.transcribe("antiFOOkomunista") == \
        [('a', 'n', 't', 'I', 'f', 'o', 'o', 'k', 'o', 'm', 'u', 'J', 'I', 's', 't', 'a')]
    # a no-op rule with a longer match trigger should make sure that this is
    # not rewritten by the tip → typ rule...
    assert cs.transcribe("tipec") == [('c', 'I', 'p', 'E', 't_s')]
    # ... while this is
    assert cs.transcribe("tipovat") == [('t', 'I', 'p', 'o', 'v', 'a', 't')]
    # franco is rewritten...
    assert cs.transcribe("franco") == [('f', 'r', 'a', 'N', 'k', 'o')]
    # ... but only when a full match
    assert cs.transcribe("francouz") == [('f', 'r', 'a', 'n', 't_s', 'o_u', 's')]
    # no voicing assimilation
    assert cs.transcribe("tbilisi") == [('t', 'b', 'I', 'l', 'I', 's', 'I')]
    # no diphthong
    assert cs.transcribe("používat") == [('p', 'o', 'u', 'Z', 'i:', 'v', 'a', 't')]
    # no hiatus
    assert cs.transcribe("využívat") == [('v', 'I', 'u', 'Z', 'i:', 'v', 'a', 't')]
    # preventing deduplication
    assert cs.transcribe("odděl") == [('o', 'd', 'J\\', 'E', 'l')]
    assert cs.transcribe("odtáhni") == [('o', 't', 't', 'a:', 'h\\', 'J', 'I')]
