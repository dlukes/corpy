"""Tokenizing, tagging and parsing text with UDPipe.

"""
import warnings

from ufal import udpipe

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
    :type model_path: str or pathlib.Path

    """

    def __init__(self, model_path):
        self._model = udpipe.Model.load(str(model_path))
        if self._model is None:
            raise RuntimeError(f"Unable to load model from {model_path!r}!")
        self._default = self._model.DEFAULT

    def process(self, text, *, tag=True, parse=True, in_format=None, out_format=None):
        """Process input text, yielding sentences one by one.

        The text is always at least tokenized, and optionally morphologically
        tagged and syntactically parsed, depending on the values of the ``tag``
        and ``parse`` arguments.

        :param text: Text to process.
        :type text: str
        :param tag: Perform morphological tagging.
        :type tag: bool
        :param parse: Perform syntactic parsing.
        :type parse: bool
        :param in_format: Input format (cf. below for possible values).
        :type in_format: None or str
        :param out_format: Output format (cf. below for possible values).
        :type out_format: None or str

        The input text is a string in one of the following formats (specified
        by ``in_format``):

        - ``None``: freeform text, which will be sentence split and tokenized
          by UDPipe
        - ``"conllu"``: the CoNLL-U_ format
        - ``"horizontal"``: one sentence per line, word forms separated by
          spaces
        - ``"vertical"``: one word per line, empty lines denote sentence ends

        .. _CoNLL-U: https://universaldependencies.org/docs/format.html

        The output format is specified by ``out_format``:

        - ``None``: native :mod:`ufal.udpipe` objects, suitable for further
          manipulation in Python
        - ``"conllu"``, ``"horizontal"`` or ``"vertical"``: cf. above
        - ``"epe"``: the EPE (Extrinsic Parser Evaluation 2017) interchange
          format
        - ``"matxin"``: the Matxin XML format
        - ``"plaintext"``: reconstruct text with original spaces, discarding
          annotations

        New input and output formats may be added with new releases of UDPipe;
        for an up-to-date list, consult the `UDPipe API reference
        <http://ufal.mff.cuni.cz/udpipe/api-reference>`__.

        """
        if in_format is None:
            in_format = self._model.newTokenizer(self._default)
        else:
            in_format = udpipe.InputFormat.newInputFormat(in_format)
            if in_format is None:
                raise RuntimeError(f"Cannot create input format {in_format!r}.")

        if out_format is not None:
            out_format = udpipe.OutputFormat.newOutputFormat(out_format)
            if out_format is None:
                raise RuntimeError(f"Cannot create output format {out_format!r}.")

        in_format.setText(text)
        error = udpipe.ProcessingError()
        sent = udpipe.Sentence()
        while in_format.nextSentence(sent, error):
            if tag:
                self.tag(sent)
            if parse:
                self.parse(sent)
            if out_format is None:
                yield sent
            else:
                yield out_format.writeSentence(sent)
            sent = udpipe.Sentence()
        if error.occurred():
            raise UdpipeError(error.message)
        if out_format is not None:
            end = out_format.finishDocument()
            if end != "":
                yield end

    def tag(self, sent):
        """Perform morphological tagging on sentence.

        Modifies ``sent`` in place.

        :param sent: Sentence to tag.
        :type sent: ufal.udpipe.Sentence

        """
        # NOTE: like InputFormat.nextSentence, Model.tag and Model.parse accept
        # a ProcessingError argument. However, the udpipe_model.py example in
        # the UDPipe repo only passes the error argument to nextSentence,
        # probably on the assumption that input format errors are the only ones
        # which can be caused by users (and therefore will also routinely have
        # to be resolved by them). Other errors are bugs which should be fixed
        # by UDPipe maintainers, so they're ignored for simplicity's sake. For
        # the time being, we follow the same rationale here.
        self._model.tag(sent, self._default)

    def parse(self, sent):
        """Perform syntactic parsing on sentence.

        Modifies ``sent`` in place.

        :param sent: Sentence to parse.
        :type sent: ufal.udpipe.Sentence

        """
        self._model.parse(sent, self._default)


def load(corpus, in_format="conllu"):
    """Load corpus in input format.

    :param corpus: The data to load.
    :type corpus: str
    :param in_format: Cf. the documentation of :meth:`Model.process`.
    :type in_format: str
    :return: A generator of sentences (:class:`ufal.udpipe.Sentence`).

    """
    in_format = udpipe.InputFormat.newInputFormat(in_format)
    if in_format is None:
        raise RuntimeError(f"Cannot create input format {in_format!r}.")
    in_format.setText(corpus)
    error = udpipe.ProcessingError()
    sent = udpipe.Sentence()
    while in_format.nextSentence(sent, error):
        yield sent
        sent = udpipe.Sentence()
    if error.occurred():
        raise UdpipeError(error.message)


def dump(sent_or_sents, out_format="conllu"):
    """Dump sentence or sentences in output format.

    :param sent_or_sents: The data to dump.
    :type corpus: :class:`ufal.udpipe.Sentence`, or iterable thereof
    :param out_format: Cf. the documentation of :meth:`Model.process`.
    :type out_format: str
    :return: A generator of strings, corresponding to the serialized sentences.
        One final additional string may contain any closing markup, if required
        by the output format.

    """
    out_format = udpipe.OutputFormat.newOutputFormat(out_format)
    if out_format is None:
        raise RuntimeError(f"Cannot create output format {out_format!r}.")

    if isinstance(sent_or_sents, udpipe.Sentence):
        yield out_format.writeSentence(sent_or_sents)
    else:
        for sent in sent_or_sents:
            yield out_format.writeSentence(sent)
    end = out_format.finishDocument()
    if end != "":
        yield end


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
    with printer.group(1, "[", "]"):
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
        warnings.warn("Please install the IPython package for pretty-printing to work.")


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
        _plain_formatter = _ipython.display_formatter.formatters["text/plain"]
        _register_pprinters(_plain_formatter)
    else:
        warnings.warn(
            "IPython session not found! Processed text will not be automatically pretty-printed, "
            "but you may still do so explicitly with the corpy.udpipe.pprint function."
        )
except ImportError:
    warnings.warn(
        "IPython package not found! Processed text will not be automatically pretty-printed, and "
        "the corpy.udpipe.pprint function will not work."
    )
