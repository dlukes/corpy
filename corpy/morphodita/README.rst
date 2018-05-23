================
corpy.morphodita
================

.. _overview:

Overview
========

A slightly more (newbie) user friendly but also probably somewhat less efficient
wrapper around the default Swig-generated Python bindings for the `MorphoDiTa
<https://github.com/ufal/morphodita>`_ morphological tagging and lemmatization
framework.

The target audience are:

- beginner programmers interested in NLP
- seasoned programmers who want to use MorphoDiTa through a more Pythonic
  interface, without having to dig into the `API reference
  <http://ufal.mff.cuni.cz/morphodita/api-reference>`_ and the `examples
  <https://github.com/ufal/morphodita/tree/master/bindings/python/examples>`_,
  and who are not too worried about a possible performance hit as compared with
  full manual control

Pre-trained tagging models which can be used with (Py)MorphoDiTa can be found
`here <http://ufal.mff.cuni.cz/morphodita#language_models>`_. Currently, Czech
and English models are available. **Please respect their CC BY-NC-SA 3.0
license!**

At the moment, only a subset of the functionality offered by the MorphoDiTa API
is available through PyMorphoDiTa (tagging features).

Usage
=====

If stuck, check out the docstrings of the modules and objects in the package
for more details. Or directly the code, they're just straightforward wrappers,
not rocket science :)

Tokenization
------------

In addition to tokenization, the MorphoDiTa tokenizers perform sentence
splitting at the same time.

The easiest way to get started is to import one of the following
pre-instantiated tokenizers from ``pymorphodita.tokenizer``: ``vertical``,
``czech``, ``english`` or ``generic``, and use it like so:

.. code:: python

   >>> from corpy.morphodita.tokenizer import generic
   >>> for sentence in generic.tokenize("foo bar baz"):
   ...     print(sentence)
   ...
   ['foo', 'bar', 'baz']


Tagging
-------

**NOTE**: Unlike tokenization, tagging in MorphoDiTa requires you to supply
your own pre-trained tagging models (see :ref:`overview` above).

Initialize a new tagger:

.. code:: python

   >>> from corpy.morphodita import Tagger
   >>> t = Tagger("path/to/czech-morfflex-pdt-160310.tagger")

Sentence split, tokenize, tag and lemmatize a text represented as a string:

.. code:: python

   >>> list(t.tag("Je zima. Bude sněžit."))
   [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
    Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
    Token(word='.', lemma='.', tag='Z:-------------'),
    Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
    Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
    Token(word='.', lemma='.', tag='Z:-------------')]
   >>> list(t.tag("Je zima. Bude sněžit.", sents=True))
   [[Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
     Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
     Token(word='.', lemma='.', tag='Z:-------------')],
    [Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
     Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
     Token(word='.', lemma='.', tag='Z:-------------')]]

Tag and lemmatize an already sentence-split and tokenized piece of text,
represented as an iterable of iterables of strings:

.. code:: python

   >>> list(t.tag([['Je', 'zima', '.'], ['Bude', 'sněžit', '.']]))
   [Token(word='Je', lemma='být', tag='VB-S---3P-AA---'),
    Token(word='zima', lemma='zima-1', tag='NNFS1-----A----'),
    Token(word='.', lemma='.', tag='Z:-------------'),
    Token(word='Bude', lemma='být', tag='VB-S---3F-AA---'),
    Token(word='sněžit', lemma='sněžit_:T', tag='Vf--------A----'),
    Token(word='.', lemma='.', tag='Z:-------------')]
