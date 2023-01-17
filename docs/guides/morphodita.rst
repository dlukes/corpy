=====================================
Tokenize and tag text with MorphoDiTa
=====================================

.. _overview:

Overview
========

The :mod:`corpy.morphodita` sub-package offers a more user friendly wrapper
around the default Swig-generated Python bindings for the `MorphoDiTa
<https://github.com/ufal/morphodita>`__ morphological tagging and lemmatization
framework.

The target audiences are:

- beginner programmers interested in NLP
- seasoned programmers who want to use MorphoDiTa through a more Pythonic
  interface, without having to dig into the `API reference
  <http://ufal.mff.cuni.cz/morphodita/api-reference>`__ and the `examples
  <https://github.com/ufal/morphodita/tree/master/bindings/python/examples>`__,
  and who are not too worried about a possible performance hit as compared with
  full manual control

Pre-trained tagging models which can be used with MorphoDiTa can be found
`here <http://ufal.mff.cuni.cz/morphodita#language_models>`__. Currently, Czech
and English models are available. **Please respect their CC BY-NC-SA 3.0
license!**

At the moment, only a subset of the functionality offered by the MorphoDiTa API
is available through :mod:`corpy.morphodita` (tokenization, tagging).

If stuck, check out the module's :mod:`API reference <corpy.morphodita>` for
more details.

Tokenization
============

When instantiating a :class:`~corpy.morphodita.Tokenizer`, pass in a string
which will determine the type of tokenizer to create. Valid options are
``"czech"``, ``"english"``, ``"generic"`` and ``"vertical"`` (cf. also the
``new_*_tokenizer`` methods in the `MorphoDiTa API reference
<http://ufal.mff.cuni.cz/morphodita/api-reference#tokenizer>`__).

.. code:: python

   >>> from corpy.morphodita import Tokenizer
   >>> tokenizer = Tokenizer("generic")
   >>> for word in tokenizer.tokenize("foo bar baz"):
   ...     print(word)
   ...
   foo
   bar
   baz

Alternatively, if you want to use the tokenizer associated with a MorphoDiTa
:file:`*.tagger` file you have available, you can instantiate it using
:meth:`~corpy.morphodita.Tokenizer.from_tagger`.

If you're interested in sentence boundaries too, pass ``sents=True`` to
:meth:`~corpy.morphodita.Tokenizer.tokenize`:

.. code:: python

   >>> for sentence in tokenizer.tokenize("foo bar baz", sents=True):
   ...     print(sentence)
   ...
   ['foo', 'bar', 'baz']

Tagging
=======

**NOTE**: Unlike tokenization, tagging in MorphoDiTa requires you to supply
your own pre-trained tagging models (see :ref:`overview` above).

Initialize a new tagger:

.. code:: python

   >>> from corpy.morphodita import Tagger
   >>> tagger = Tagger("./czech-morfflex-pdt.tagger")

Tokenize, tag and lemmatize a text represented as a string:

.. code:: python

   >>> from pprint import pprint
   >>> tokens = list(tagger.tag("Je zima. Bude sněžit."))
   >>> pprint(tokens)
   [Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
    Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
    Token(word='.', lemma='.', tag='Z:-------------'),
    Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
    Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
    Token(word='.', lemma='.', tag='Z:-------------')]

With sentence boundaries:

.. code:: python

   >>> sents = list(tagger.tag("Je zima. Bude sněžit.", sents=True))
   >>> pprint(sents)
   [[Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
     Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
     Token(word='.', lemma='.', tag='Z:-------------')],
    [Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
     Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
     Token(word='.', lemma='.', tag='Z:-------------')]]

Tag and lemmatize an already sentence-split and tokenized piece of text,
represented as an iterable of iterables of strings:

.. code:: python

   >>> tokens = list(tagger.tag([['Je', 'zima', '.'], ['Bude', 'sněžit', '.']]))
   >>> pprint(tokens)
   [Token(word='Je', lemma='být', tag='VB-S---3P-AAI--'),
    Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
    Token(word='.', lemma='.', tag='Z:-------------'),
    Token(word='Bude', lemma='být', tag='VB-S---3F-AAI--'),
    Token(word='sněžit', lemma='sněžit', tag='Vf--------A-I--'),
    Token(word='.', lemma='.', tag='Z:-------------')]
