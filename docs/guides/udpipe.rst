==============================
Tag and parse text with UDPipe
==============================

**NOTE:** When playing around with UDPipe interactively, it's highly recommended
to use IPython_ or a Jupyter_ notebook. You'll automatically get nice
pretty-printing.

.. _IPython: https://ipython.org/
.. _Jupyter: https://jupyter.org/

Overview
========

UDPipe_ is a fast and convenient library for stochastic morphological tagging
(including lemmatization) and syntactic parsing of text. :mod:`corpy.udpipe`
aims to give easy access to the most commonly used features of the library; for
more advanced use cases, you might need to use the more lower-level ufal.udpipe_
package, on top of which this module is built.

.. _UDPipe: http://ufal.mff.cuni.cz/udpipe
.. _ufal.udpipe: https://pypi.org/project/ufal.udpipe/

In order to use UDPipe, you need a pre-trained model for your language of
interest. Models are available for many languages, for more information, refer
to the `UDPipe website <http://ufal.mff.cuni.cz/udpipe/models>`__. **When using
the models, please make sure to respect their CC BY-NC-SA license!**

In order to better understand how UDPipe represents tagged and parsed text, it
is useful to familiarize yourself with the CoNLL-U_ data format. UDPipe data
structures (sentences, words, multi-word tokens, empty nodes, comments) map onto
concepts defined in this format.

.. _CoNLL-U: https://universaldependencies.org/format.html

In addition to this guide, there is also an :mod:`API reference
<corpy.udpipe>` for :mod:`corpy.udpipe`. For an overview of the API of
underlying :mod:`ufal.udpipe` objects (listing available attributes and
methods), see `here <https://pypi.org/project/ufal.udpipe/>`__.

Processing text
===============

Tagging and parsing text using UDPipe is fairly simple. Just load a UDPipe
:class:`~corpy.udpipe.Model`:

.. code:: python

   >>> from corpy.udpipe import Model
   >>> m = Model("./czech-pdt-ud-2.4-190531.udpipe")

And process some text using the :meth:`~corpy.udpipe.Model.process` method (the
method creates a generator, so you'll need e.g. :func:`list` to tease all of the
elements out of it):

.. code:: python

   >>> sents = list(m.process("Je zima. Bude sněžit."))
   >>> sents
   [<Swig Object of type 'sentence *' at 0x...>, <Swig Object of type 'sentence *' at 0x...>]

Ouch. This output is not really helpful. This is why it's recommended to use
IPython_ or Jupyter_, because at a regular Python REPL, the output of UDPipe is
rendered as opaque Swig_ objects.

.. _Swig: http://www.swig.org/

However, if the IPython package is at least installed, you can explicitly
pretty-print the output using the :func:`~corpy.udpipe.pprint` function:

.. code:: python

   >>> from corpy.udpipe import pprint
   >>> pprint(sents)
   [Sentence(
      comments=['# newdoc', '# newpar', '# sent_id = 1', '# text = Je zima.'],
      words=[
        Word(id=0, <root>),
        Word(id=1,
             form='Je',
             lemma='být',
             xpostag='VB-S---3P-AA---',
             upostag='VERB',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act',
             head=0,
             deprel='root'),
        Word(id=2,
             form='zima',
             lemma='zima',
             xpostag='NNFS1-----A----',
             upostag='NOUN',
             feats='Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos',
             head=1,
             deprel='nsubj',
             misc='SpaceAfter=No'),
        Word(id=3,
             form='.',
             lemma='.',
             xpostag='Z:-------------',
             upostag='PUNCT',
             head=1,
             deprel='punct')]),
    Sentence(
      comments=['# sent_id = 2', '# text = Bude sněžit.'],
      words=[
        Word(id=0, <root>),
        Word(id=1,
             form='Bude',
             lemma='být',
             xpostag='VB-S---3F-AA---',
             upostag='AUX',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Fut|VerbForm=Fin|Voice=Act',
             head=2,
             deprel='aux'),
        Word(id=2,
             form='sněžit',
             lemma='sněžit',
             xpostag='Vf--------A----',
             upostag='VERB',
             feats='Aspect=Imp|Polarity=Pos|VerbForm=Inf',
             head=0,
             deprel='root',
             misc='SpaceAfter=No'),
        Word(id=3,
             form='.',
             lemma='.',
             xpostag='Z:-------------',
             upostag='PUNCT',
             head=2,
             deprel='punct',
             misc='SpaceAfter=No')])]

Much better! And again, calling ``pprint(sents)`` is not necessary when using
IPython_ or Jupyter_, you can just evaluate ``sents`` and it will be
pretty-printed automatically.

Pretty-printing options
=======================

The output of UDPipe can be quite verbose -- the individual objects have many
fields. However, some values are not really that interesting (e.g. the empty
string for string attributes, or ``-1`` for integer attributes). Therefore, they
are hidden by the pretty-printer by default, so as to make the output more
concise.

Sometimes though, you might want exhaustive pretty-printing, e.g. to learn about
all of the possible attributes, even though your output doesn't happen to have
any useful values in them. In order to do that, disable the ``digest`` option
using the :func:`~corpy.udpipe.pprint_config` function:

.. code:: python

   >>> from corpy.udpipe import pprint_config
   >>> pprint_config(digest=False)
   >>> pprint(sents)
   [Sentence(
      comments=['# newdoc', '# newpar', '# sent_id = 1', '# text = Je zima.'],
      words=[
        Word(id=0,
             form='<root>',
             lemma='<root>',
             xpostag='<root>',
             upostag='<root>',
             feats='<root>',
             head=-1,
             deprel='',
             deps='',
             misc=''),
        Word(id=1,
             form='Je',
             lemma='být',
             xpostag='VB-S---3P-AA---',
             upostag='VERB',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act',
             head=0,
             deprel='root',
             deps='',
             misc=''),
        Word(id=2,
             form='zima',
             lemma='zima',
             xpostag='NNFS1-----A----',
             upostag='NOUN',
             feats='Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos',
             head=1,
             deprel='nsubj',
             deps='',
             misc='SpaceAfter=No'),
        Word(id=3,
             form='.',
             lemma='.',
             xpostag='Z:-------------',
             upostag='PUNCT',
             feats='',
             head=1,
             deprel='punct',
             deps='',
             misc='')],
      multiwordTokens=[],
      emptyNodes=[]),
    Sentence(
      comments=['# sent_id = 2', '# text = Bude sněžit.'],
      words=[
        Word(id=0,
             form='<root>',
             lemma='<root>',
             xpostag='<root>',
             upostag='<root>',
             feats='<root>',
             head=-1,
             deprel='',
             deps='',
             misc=''),
        Word(id=1,
             form='Bude',
             lemma='být',
             xpostag='VB-S---3F-AA---',
             upostag='AUX',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Fut|VerbForm=Fin|Voice=Act',
             head=2,
             deprel='aux',
             deps='',
             misc=''),
        Word(id=2,
             form='sněžit',
             lemma='sněžit',
             xpostag='Vf--------A----',
             upostag='VERB',
             feats='Aspect=Imp|Polarity=Pos|VerbForm=Inf',
             head=0,
             deprel='root',
             deps='',
             misc='SpaceAfter=No'),
        Word(id=3,
             form='.',
             lemma='.',
             xpostag='Z:-------------',
             upostag='PUNCT',
             feats='',
             head=2,
             deprel='punct',
             deps='',
             misc='SpaceAfter=No')],
      multiwordTokens=[],
      emptyNodes=[])]

Input and output formats
========================

UDPipe supports a variety of input and output formats. For convenience, they are
listed in the documentation of the :meth:`corpy.udpipe.Model.process` method,
but the most up-to-date, reference list is always available in the `UDPipe API
docs <http://ufal.mff.cuni.cz/udpipe/api-reference>`__.

One format which is particularly useful is the CoNLL-U_ format: it's the format
of the UniversalDependencies_ project, and as such, it's intimately associated
with UDPipe, which is also part of the project. Reading up on the CoNLL-U_
format can help you better understand how UDPipe represents tagged and parsed
text, especially some of the less straightforward features (e.g. `multi-word
tokens and empty nodes
<https://universaldependencies.org/format.html#words-tokens-and-empty-nodes>`__).

.. _UniversalDependencies: https://universaldependencies.org

Say you have a small two-sentence corpus in the "horizontal" format (one
sentence per line, words separated by spaces), and you want to tag it, parse it,
and output it in the CoNLL-U format. You can do it like so:

.. code:: python

   >>> horizontal = """Je zima.
   ... Bude sněžit."""
   >>> conllu_sents = list(m.process(horizontal, in_format="horizontal", out_format="conllu"))
   >>> conllu_sents
   ['# newdoc\n# newpar\n# sent_id = 1\n1\tJe\tbýt\tVERB\tVB-S---3P-AA---\tMood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act\t0\troot\t_\t_\n2\tzima.\tzima.\tPUNCT\tZ:-------------\t_\t1\tpunct\t_\t_\n\n', '# sent_id = 2\n1\tBude\tbýt\tVERB\tVB-S---3F-AA---\tMood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Fut|VerbForm=Fin|Voice=Act\t0\troot\t_\t_\n2\tsněžit.\tsněžit.\tPUNCT\tZ:-------------\t_\t1\tpunct\t_\t_\n\n']

That's a bit messy, but trust me that ``conllu_sents`` is just a list of two
strings, each string representing one sentence. Or, if you don't trust me:

.. code:: python

   >>> len(conllu_sents)
   2
   >>> [type(x) for x in conllu_sents]
   [<class 'str'>, <class 'str'>]

To give you an idea of the format, let's just join the sentences and print them
out:

.. code:: python

   >>> print("".join(conllu_sents), end="")  # doctest: +NORMALIZE_WHITESPACE
   # newdoc
   # newpar
   # sent_id = 1
   1	Je	být	VERB	VB-S---3P-AA---	Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_
   2	zima.	zima.	PUNCT	Z:-------------	_	1	punct	_	_
   <BLANKLINE>
   # sent_id = 2
   1	Bude	být	VERB	VB-S---3F-AA---	Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Fut|VerbForm=Fin|Voice=Act	0	root	_	_
   2	sněžit.	sněžit.	PUNCT	Z:-------------	_	1	punct	_	_
   <BLANKLINE>
