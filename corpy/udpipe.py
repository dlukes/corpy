"""Tokenizing, tagging and parsing text with UDPipe.

"""
import logging

from ufal import udpipe

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

WORD_ATTRS = (
    "id",
    "form",
    "lemma",
    "xpostag",
    "upostag",
    "feats",
    "head",
    "deprel",
    "deps",
    "misc",
)
MULTIWORDTOKEN_ATTRS = ("idFirst", "idLast", "form", "misc")
EMPTYNODE_ATTRS = (
    "id",
    "index",
    "form",
    "lemma",
    "upostag",
    "xpostag",
    "feats",
    "deps",
    "misc",
)
SENT_ATTRS = ("comments", "words", "multiwordTokens", "emptyNodes")
PPRINT_DIGEST = True


class UdpipeError(Exception):
    """An error which occurred in the :mod:`ufal.udpipe` C extension."""


class Model:
    """A UDPipe model for tagging and parsing text.

    :param model_path: Path to the pre-compiled UDPipe model to load.
    :type model_path: str

    """

    def __init__(self, model_path):
        LOG.info("Loading model.")
        self._model = udpipe.Model.load(model_path)
        if self._model is None:
            raise RuntimeError(f"Unable to load model from {model_path!r}!")

    def process(self, text, *, in_format="tokenize", tag=True, parse=True):
        """Process input text, yielding sentences one by one.

        The text is always at least tokenized, and optionally morphologically
        tagged and syntactically parsed, depending on the values of the ``tag``
        and ``parse`` arguments.

        :param text: Text to process.
        :type text: str
        :param in_format: Input format (cf. below for possible values).
        :type in_format: str
        :param tag: Perform morphological tagging.
        :type tag: bool
        :param parse: Perform syntactic parsing.
        :type parse: bool

        The input text is a string in one of the following formats (specified
        by ``in_format``):

        - ``"tokenize"``: freeform text, which will be sentence split and
          tokenized by UDPipe
        - ``"conllu"``: the `CoNLL-U <https://universaldependencies.org/docs/format.html>`__
          format
        - ``"horizontal"``: one sentence per line, word forms separated by
          spaces
        - ``"vertical"``: one word per line, empty lines denote sentence ends

        """
        default = self._model.DEFAULT
        if in_format == "tokenize":
            in_format = self._model.newTokenizer(default)
        else:
            in_format = udpipe.InputFormat.newInputFormat(in_format)
        if not in_format:
            raise RuntimeError(f"Cannot create input format {in_format!r}.")
        in_format.setText(text)
        error = udpipe.ProcessingError()
        sent = udpipe.Sentence()
        while in_format.nextSentence(sent, error):
            if tag:
                self._model.tag(sent, default)
            if parse:
                self._model.parse(sent, default)
            yield sent
            sent = udpipe.Sentence()
            if error.occurred():
                raise UdpipeError(error.message)


def _pprint_token(token, printer, cycle):
    cls_name = type(token).__name__
    if cycle:
        return printer.text(f"{cls_name}(...)")
    elif PPRINT_DIGEST and token.form == "<root>":
        return printer.text(f"{cls_name}(id={token.id}, <root>)")
    indent = len(cls_name) + 1
    with printer.group(indent, f"{cls_name}(", ")"):
        i = 0
        for attr in globals()[cls_name.upper() + "_ATTRS"]:
            val = getattr(token, attr)
            if not PPRINT_DIGEST or val != "" and val != -1:
                if i:
                    printer.text(",")
                    printer.breakable()
                printer.text(f"{attr}={val!r}")
                i += 1


def _pprint_sent(sent, printer, cycle):
    if cycle:
        return printer.text("Sentence(...)")
    with printer.group(2, "Sentence(", ")"):
        for i, attr in enumerate(SENT_ATTRS):
            seq = getattr(sent, attr)
            if PPRINT_DIGEST and seq.size() == 0:
                continue
            if i:
                printer.text(",")
            printer.breakable("")
            with printer.group(2, f"{attr}=[", "]"):
                printer.breakable("")
                for j, elem in enumerate(seq):
                    if j:
                        printer.text(",")
                        printer.breakable()
                    printer.pretty(elem)


def _pprint_seq(seq, printer, cycle):
    if cycle:
        return printer.text("[...]")
    # NOTE: The following is basically the same code as at the end of
    # _pprint_sent, minus a call to printer.breakable("") just after the with,
    # the indent width and the starting delimiter string of the group.
    # Unfortunately, I haven't yet figured out a way to adjust this depending
    # on whether _pprint_seq is called from _pprint_sent or not, so it will
    # have to stay duplicated for the time being.
    with printer.group(1, f"[", "]"):
        for j, elem in enumerate(seq):
            if j:
                printer.text(",")
                printer.breakable()
            printer.pretty(elem)


def pprint(obj):
    """Pretty-print object.

    This is a convenience wrapper over :func:`IPython.lib.pretty.pprint` for
    easier importing.

    """
    try:
        from IPython.lib import pretty

        pretty.pprint(obj)
    except ImportError:
        LOG.warning("Please install the IPython package for pretty-printing to work.")


def pprint_config(*, digest=True):
    """Configure pretty-printing of :mod:`ufal.udpipe` objects.

    :param digest: Show only attributes with interesting values (other than
        ``''`` or ``-1``)
    :type digest: bool

    """
    global PPRINT_DIGEST
    PPRINT_DIGEST = digest


def _register_pprinters(formatter):
    formatter.for_type(udpipe.Word, _pprint_token)
    formatter.for_type(udpipe.MultiwordToken, _pprint_token)
    formatter.for_type(udpipe.EmptyNode, _pprint_token)
    formatter.for_type(udpipe.Sentence, _pprint_sent)
    formatter.for_type(udpipe.Comments, _pprint_seq)
    formatter.for_type(udpipe.Words, _pprint_seq)
    formatter.for_type(udpipe.MultiwordTokens, _pprint_seq)
    formatter.for_type(udpipe.EmptyNodes, _pprint_seq)


try:
    from IPython import get_ipython
    from IPython.lib import pretty

    _register_pprinters(pretty)
    _ipython = get_ipython()  # pylint: disable=invalid-name
    if _ipython is not None:
        _plain_formatter = _ipython.display_formatter.formatters[  # pylint: disable=invalid-name
            "text/plain"
        ]
        _register_pprinters(_plain_formatter)
    else:
        LOG.warning(
            "IPython session not found! Processed text will not be automatically pretty-printed, "
            "but you may still do so explicitly with the corpy.udpipe.pprint function."
        )
except ImportError:
    LOG.warning(
        "IPython package not found! Processed text will not be automatically pretty-printed, and "
        "the corpy.udpipe.pprint function will not work."
    )
