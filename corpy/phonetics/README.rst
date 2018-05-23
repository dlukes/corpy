===============
corpy.phonetics
===============

Overview
========

Doing phonetics with Python.

Czech rule-based grapheme-to-phoneme conversion
===============================================

In addition to rules, an exception system is also implemented which makes it
possible to capture less regular pronunciation patterns.

Usage
-----

The simplest public interface is the ``transcribe`` function. See its
docstring for more information on the types of accepted input as well as on
output options and other available customizations. Here are a few usage
examples -- default output is SAMPA:

.. code:: python

   >>> from corpy.phonetics import cs
   >>> cs.transcribe("máš hlad")
   [('m', 'a:', 'Z'), ('h\\', 'l', 'a', 't')]

But other options including IPA are available:

.. code:: python

   >>> cs.transcribe("máš hlad", alphabet="IPA")
   [('m', 'aː', 'ʒ'), ('ɦ', 'l', 'a', 't')]

Hyphens can be used to prevent interactions between neighboring phones, e.g.
assimilation of voicing:

.. code:: python

   >>> cs.transcribe("máš- hlad")

Tokens containing non-alphabetic characters (except for hyphens) are passed
through as is:

.. code:: python

   >>> cs.transcribe("máš ? hlad")
   [('m', 'a:', 'Z'), '?', ('h\\', 'l', 'a', 't')]

And you can even configure some of them to constitute a blocking boundary for
interactions between phones (notice that unlike in the previous example,
"máš" ends with a /S/ → assimilation of voicing wasn't allowed to spread
past the ".."):

.. code:: python

   >>> cs.transcribe("máš .. hlad", prosodic_boundary_symbols={".."})
   [('m', 'a:', 'S'), '..', ('h\\', 'l', 'a', 't')]

Finally, when the input is a single string, it's simply split on whitespace,
but you can also provide your own tokenization. E.g. if your input string
contains square brackets to mark overlapping speech, this is probably not the
output you want:

.. code:: python

   >>> cs.transcribe("[máš] hlad")
   ['[máš]', ('h\\', 'l', 'a', 't')]

But if you pretokenize the input yourself according to rules that make sense
in your situation, you're good to go:

.. code:: python

   >>> cs.transcribe(["[", "máš", "]", "hlad"])
   ['[', ('m', 'a:', 'Z'), ']', ('h\\', 'l', 'a', 't')]

Acknowledgments
===============

The choice of (X-)SAMPA and IPA transcription symbols follows the `guidelines
<https://fonetika.ff.cuni.cz/o-fonetice/foneticka-transkripce/czech-sampa/>`_
published by the Institute of Phonetics, Faculty of Arts, Charles University,
Prague, which are hereby gratefully acknowledged.
