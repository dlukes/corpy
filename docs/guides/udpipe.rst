==============================
Tag and parse text with UDPipe
==============================

**NOTE:** When playing around with UDPipe interactively, it's highly recommended
to use IPython_ or a Jupyter_ notebook. You'll automatically get nice
pretty-printing.

Overview
========

UDPipe_ is a fast and convenient library for morphological tagging and syntactic
parsing of text.  :mod:`corpy.udpipe` aims to give easy access to the most
commonly used features of the library; for more advanced use cases, you might
need to use the more lower-level ufal.udpipe_ package, on top of which this
module is built.

In addition to this guide, there is also an :mod:`API reference
<corpy.udpipe>` for :mod:`corpy.udpipe`. For an overview of the API of
underlying :mod:`ufal.udpipe` objects (listing available attributes and
methods), see `here <https://pypi.org/project/ufal.udpipe/>`__.

In order to use UDPipe, you need a pre-trained model for your language of
interest. Models are available for many languages, for more information, refer
to the `UDPipe website <http://ufal.mff.cuni.cz/udpipe/models>`__. **When using
them, please make sure to respect their CC BY-NC-SA license!**

Processing text
===============

Tagging and parsing text using UDPipe is fairly simple. Just load a UDPipe
:class:`~corpy.udpipe.Model`:

.. code:: python

   >>> from corpy.udpipe import Model
   >>> m = Model("./czech-pdt-ud-2.3-181115.udpipe")

And process some text using the :meth:`~corpy.udpipe.Model.process` method (the
method creates a generator, so you'll need e.g. :func:`list` to tease all of the
elements out of it):

.. code:: python

   >>> sents = list(m.process("Je zima. Bude sněžit."))
   >>> sents
   [<Swig Object of type 'sentence *' at 0x...>, <Swig Object of type 'sentence *' at 0x...>]

Ouch. Not really helpful. This is why it's recommended to use IPython_ or
Jupyter_, because at a regular Python REPL, the output of UDPipe is rendered as
opaque Swig_ objects.

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
             upostag='AUX',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act',
             head=2,
             deprel='cop'),
        Word(id=2,
             form='zima',
             lemma='zima',
             xpostag='NNFS1-----A----',
             upostag='NOUN',
             feats='Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos',
             head=0,
             deprel='root',
             misc='SpaceAfter=No'),
        Word(id=3,
             form='.',
             lemma='.',
             xpostag='Z:-------------',
             upostag='PUNCT',
             head=2,
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
             upostag='AUX',
             feats='Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act',
             head=2,
             deprel='cop',
             deps='',
             misc=''),
        Word(id=2,
             form='zima',
             lemma='zima',
             xpostag='NNFS1-----A----',
             upostag='NOUN',
             feats='Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos',
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

Input formats
=============

Output formats
==============

.. _IPython: https://ipython.org/
.. _Jupyter: https://jupyter.org/
.. _UDPipe: http://ufal.mff.cuni.cz/udpipe
.. _ufal.udpipe: https://pypi.org/project/ufal.udpipe/
.. _Swig: http://www.swig.org/
