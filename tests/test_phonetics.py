import pytest
from pathlib import Path

from corpy.phonetics import cs
from corpy.morphodita import Tagger

SCRIPT_DIR = Path(__file__).parent
TAGGER = Tagger(SCRIPT_DIR.parent / "czech-morfflex-pdt-161115.tagger")


def test_voicing_assimilation_over_word_boundaries():
    assert cs.transcribe("máš hlad") == [("m", "a:", "Z"), ("h\\", "l", "a", "t")]


@pytest.mark.parametrize(
    "orth,phon",
    [
        ("pařát", [("p", "a", "P\\", "a:", "t")]),
        ("přát", [("p", "Q\\", "a:", "t")]),
        ("hřát", [("h\\", "P\\", "a:", "t")]),
    ],
)
def test_voicing_assimilation_of_ř(orth, phon):
    assert cs.transcribe(orth) == phon


@pytest.mark.parametrize(
    "orth,alphabet,phon",
    [
        (
            "máš hlad",
            "IPA",
            [
                ("m", "aː", "ʒ"),
                ("ɦ", "l", "a", "t"),
            ],
        ),
        (
            "máš hlad",
            "CS",
            [
                ("m", "á", "ž"),
                ("h", "l", "a", "t"),
            ],
        ),
        (
            "máš hlad",
            "CNC",
            [
                ("m", "á", "ž"),
                ("h", "l", "a", "t"),
            ],
        ),
    ],
)
def test_different_output_alphabets(orth, alphabet, phon):
    assert cs.transcribe(orth, alphabet=alphabet) == phon


class TestHiatus:
    def test_no_hiatus_by_default_in_most_cases(self):
        assert cs.transcribe("hiát") == [("h\\", "I", "a:", "t")]

    def test_hiatus_by_default_between_high_front_vowels(self):
        assert cs.transcribe("Indii") == [("I", "n", "d", "I", "j", "I")]

    def test_hiatus_can_be_optionally_forced(self):
        assert cs.transcribe("hiát", hiatus=True) == [("h\\", "I", "j", "a:", "t")]


@pytest.mark.parametrize(
    "orth,phon",
    [
        ("tramvaj", [("t", "r", "a", "F", "v", "a", "j")]),
        ("kongo", [("k", "o", "N", "g", "o")]),
    ],
)
def test_other_csps(orth, phon):
    assert cs.transcribe(orth) == phon


@pytest.mark.parametrize(
    "orth,phon",
    [
        ("denně", [("d", "E", "J", "E")]),
        # short vowels are exempt for obvious reasons:
        ("pootevřít", [("p", "o", "o", "t", "E", "v", "P\\", "i:", "t")]),
        ("neexistoval", [("n", "E", "E", "g", "z", "I", "s", "t", "o", "v", "a", "l")]),
        ("muzeem", [("m", "u", "z", "E", "E", "m")]),
        # but long vowels are not
        ("áá", [("a:",)]),
    ],
)
def test_remove_duplicate_graphemes(orth, phon):
    assert cs.transcribe(orth) == phon


@pytest.mark.parametrize(
    "orth,phon",
    [
        ("dražší", [("d", "r", "a", "S", "i:")]),
        # but gemination currently remains allowed across word boundaries
        ("t t", [("t",), ("t",)]),
    ],
)
def test_no_gemination(orth, phon):
    assert cs.transcribe(orth) == phon


@pytest.mark.parametrize(
    "orth,phon",
    [
        # partial replacements work as expected...
        ("cyklistický", [("t_s", "I", "k", "l", "I", "s", "t", "I", "t_s", "k", "i:")]),
        ("cyklisti", [("t_s", "I", "k", "l", "I", "s", "c", "I")]),
        # ... even with a prefix
        (
            "necyklistický",
            [("n", "E", "t_s", "I", "k", "l", "I", "s", "t", "I", "t_s", "k", "i:")],
        ),
        ("necyklisti", [("n", "E", "t_s", "I", "k", "l", "I", "s", "c", "I")]),
        # the regex is properly constructed so that longer matches win: this
        # should match komuni...
        ("komunita", [("k", "o", "m", "u", "n", "I", "t", "a")]),
        # ... this too...
        ("komunisti", [("k", "o", "m", "u", "n", "I", "s", "c", "I")]),
        # .. and this should match komunisti.
        (
            "komunistický",
            [("k", "o", "m", "u", "n", "I", "s", "t", "I", "t_s", "k", "i:")],
        ),
        # contiguous matches starting at the beginning of the string can be
        # rewritten...
        (
            "antikomunista",
            [("a", "n", "t", "I", "k", "o", "m", "u", "n", "I", "s", "t", "a")],
        ),
        # ... but once the contiguity is broken (as here by the substring FOO),
        # rewriting stops (notice -JIsta below instead of -nIsta)
        (
            "antiFOOkomunista",
            [
                (
                    "a",
                    "n",
                    "t",
                    "I",
                    "f",
                    "o",
                    "o",
                    "k",
                    "o",
                    "m",
                    "u",
                    "J",
                    "I",
                    "s",
                    "t",
                    "a",
                )
            ],
        ),
        # a no-op rule with a longer match trigger should make sure that this is
        # not rewritten by the tip → typ rule...
        ("tipec", [("c", "I", "p", "E", "t_s")]),
        # ... while this is
        ("tipovat", [("t", "I", "p", "o", "v", "a", "t")]),
        # franco is rewritten...
        ("franco", [("f", "r", "a", "N", "k", "o")]),
        # ... but only when a full match
        ("francouz", [("f", "r", "a", "n", "t_s", "o_u", "s")]),
        # no voicing assimilation
        ("tbilisi", [("t", "b", "I", "l", "I", "s", "I")]),
        # no diphthong
        ("používat", [("p", "o", "u", "Z", "i:", "v", "a", "t")]),
        # no hiatus
        ("využívat", [("v", "I", "u", "Z", "i:", "v", "a", "t")]),
        # preventing deduplication
        ("odděl", [("o", "d", "J\\", "E", "l")]),
        ("odtáhni", [("o", "t", "t", "a:", "h\\", "J", "I")]),
    ],
)
def test_exceptions(orth, phon):
    """NOTE: Use these tests as a source of inspiration as to what can be
    achieved using exceptions. The system is kind of ugly and hacky but thanks
    to that, it's also flexible.

    """
    assert cs.transcribe(orth) == phon


@pytest.mark.parametrize(
    "tokens,pros_boundaries,matrix,to_transcribe",
    [
        (
            ["foo", "-bar", "baz?"],
            set(),
            [None, None, "baz?"],
            ["foo", "-bar"],
        ),
        # a "-" is inserted in the list of tokens to transcribe at each prosodic
        # boundary; it will be removed in the process of transcription after it
        # has performed its role of blocking interaction between otherwise
        # neighboring phones
        (
            ["foo", "?", "bar"],
            {"?"},
            [None, "?", None],
            ["foo", "-", "bar"],
        ),
    ],
)
def test_separate_tokens(tokens, pros_boundaries, matrix, to_transcribe):
    assert cs._separate_tokens(tokens, pros_boundaries) == (matrix, to_transcribe)


class TestProsodicBoundaries:
    def test_no_prosodic_boundaries(self):
        # no prosodic boundaries → voicing assimilation occurs (notice "d"
        # before "?" because of following "b")
        assert cs.transcribe("máš hlad ? Bibi též") == [
            ("m", "a:", "Z"),
            ("h\\", "l", "a", "d"),
            "?",
            ("b", "I", "b", "I"),
            ("t", "E:", "S"),
        ]

    def test_double_dot_as_prosodic_boundary(self):
        # .. is a prosodic boundary → voicing assimilation is stopped (notice
        # "t" before "..")
        assert cs.transcribe(
            "máš hlad .. Bibi též", prosodic_boundary_symbols={".."}
        ) == [
            ("m", "a:", "Z"),
            ("h\\", "l", "a", "t"),
            "..",
            ("b", "I", "b", "I"),
            ("t", "E:", "S"),
        ]


class TestUserAddedHyphen:
    def test_hyphen_at_start_of_word(self):
        assert cs.transcribe("máš -hlad") == [("m", "a:", "S"), ("h\\", "l", "a", "t")]

    def test_hyphen_mid_word(self):
        assert cs.transcribe("d-štít") == [("d", "S", "c", "i:", "t")]

    def test_hyphen_at_end_of_word_is_not_allowed(self):
        with pytest.raises(ValueError) as exc_info:
            cs.transcribe("máš- hlad")
        assert "máš-" in exc_info.exconly()

    def test_some_ways_to_have_a_literal_hyphen(self):
        assert cs.transcribe("- --- ?hlad- hl?-ad etc.") == [
            "-",
            "---",
            "?hlad-",
            "hl?-ad",
            "etc.",
        ]


class TestSmartHandlingOfVowelAcrossMorphemeBoundary:
    @pytest.mark.parametrize(
        "orth,phon",
        [
            # adjacent vowels incorrectly merged into diphthong
            ("neurazit", [("n", "E_u", "r", "a", "z", "I", "t")]),
            ("praubohý", [("p", "r", "a_u", "b", "o", "h\\", "i:")]),
        ],
    )
    def test_no_tagger(self, orth, phon):
        assert cs.transcribe(orth) == phon

    @pytest.mark.parametrize(
        "orth,phon",
        [
            # adjacent vowels correctly split into monophthongs
            ("neurazit", [("n", "E", "u", "r", "a", "z", "I", "t")]),
            ("neurozený", [("n", "E", "u", "r", "o", "z", "E", "n", "i:")]),
            ("praubohý", [("p", "r", "a", "u", "b", "o", "h\\", "i:")]),
            # adjacent vowels correctly merged into diphthong
            ("neuron", [("n", "E_u", "r", "o", "n")]),
        ],
    )
    def test_with_tagger(self, orth, phon):
        assert cs.transcribe(orth, tagger=TAGGER) == phon

    # TODO: Enable these when a new MorphoDiTa model is released, with a DeriNet
    # which has useful derivations for them.
    # assert cs.transcribe("poukázat") == [("p", "o_u", "k", "a:", "z", "a", "t")]
    # assert cs.transcribe("poukázat", tagger=tagger) == [
    #     ("p", "o", "u", "k", "a:", "z", "a", "t")
    # ]
    # assert cs.transcribe("vyextrahovat", hiatus=True) == [
    #     ("v", "I", "j", "E", "k", "s", "t", "r", "a", "h\\", "o", "v", "a", "t")
    # ]
    # assert cs.transcribe("vyextrahovat", tagger=tagger, hiatus=True) == [
    #     ("v", "I", "E", "k", "s", "t", "r", "a", "h\\", "o", "v", "a", "t")
    # ]
