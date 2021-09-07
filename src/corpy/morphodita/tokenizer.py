"""An interface to MorphoDiTa tokenizers.

"""
import ufal.morphodita as ufal


class Tokenizer:
    """A wrapper API around the tokenizers offered by MorphoDiTa.

    :param tokenizer_type: Type of the requested tokenizer (cf. below for
        possible values).
    :type tokenizer_type: str

    `tokenizer_type` is typically one of:

    - ``"czech"``: a tokenizer tuned for Czech
    - ``"english"``: a tokenizer tuned for English
    - ``"generic"``: a generic tokenizer
    - ``"vertical"``: a simple tokenizer for the vertical format, which is
      effectively already tokenized (one word per line)

    Specifically, the available tokenizers are determined by the
    ``new_*_tokenizer`` static methods on the MorphoDiTa ``tokenizer`` class
    described in the `MorphoDiTa API reference
    <https://ufal.mff.cuni.cz/morphodita/api-reference#tokenizer>`__.

    """

    def __init__(self, tokenizer_type):
        constructor_name = "new" + tokenizer_type.capitalize() + "Tokenizer"
        self.tokenizer_constructor = getattr(ufal.Tokenizer, constructor_name)  # type: ignore

    @staticmethod
    def from_tagger(tagger_path):
        """Load tokenizer associated with tagger file."""
        self = Tokenizer("generic")
        tagger = ufal.Tagger.load(str(tagger_path))  # type: ignore
        self.tokenizer_constructor = tagger.newTokenizer
        if self.tokenizer_constructor() is None:
            raise RuntimeError(f"The tagger {tagger_path} has no associated tokenizer.")
        return self

    def tokenize(self, text, sents=False):
        """Tokenize `text`.

        :param text: Text to tokenize.
        :type text: str
        :param sents: Whether to signal sentence boundaries by outputting a
            sequence of lists (sentences).
        :type sents: bool
        :return: An iterator over the tokenized text, possibly grouped into
            sentences if ``sents=True``.

        Note that MorphoDiTa performs both sentence splitting and tokenization
        at the same time, but this method iterates over tokens without sentence
        boundaries by default:

        >>> from corpy.morphodita import Tokenizer
        >>> t = Tokenizer("generic")
        >>> for word in t.tokenize("foo bar baz"):
        ...     print(word)
        ...
        foo
        bar
        baz

        If you want to iterate over sentences (lists of tokens), set
        ``sents=True``:

        >>> for sentence in t.tokenize("foo bar baz", sents=True):
        ...     print(sentence)
        ...
        ['foo', 'bar', 'baz']

        """
        # this is more elegant than just segfaulting in the MorphoDiTa C++ library if None is
        # passed...
        if not isinstance(text, str):
            raise TypeError(
                "``text`` should be a str, you passed in {}.".format(type(text))
            )
        forms = ufal.Forms()  # type: ignore
        token_ranges = ufal.TokenRanges()  # type: ignore
        tokenizer = self.tokenizer_constructor()
        tokenizer.setText(text)
        while tokenizer.nextSentence(forms, token_ranges):
            if sents:
                yield list(forms)
            else:
                yield from forms
