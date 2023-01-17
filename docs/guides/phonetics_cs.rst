===================================================
Rule-based grapheme to phoneme conversion for Czech
===================================================

In addition to rules, an exception system is also implemented which makes it
possible to capture less regular pronunciation patterns.

Usage
=====

The simplest public interface is the :func:`~corpy.phonetics.cs.transcribe`
function. See its docstring for more information on the types of accepted input
as well as on output options and other available customizations. Here are a few
usage examples -- default output is SAMPA:

.. code:: python

   >>> from corpy.phonetics import cs
   >>> cs.transcribe("máš hlad")
   [('m', 'a:', 'Z'), ('h\\', 'l', 'a', 't')]

But other options including IPA are available:

.. code:: python

   >>> cs.transcribe("máš hlad", alphabet="IPA")
   [('m', 'aː', 'ʒ'), ('ɦ', 'l', 'a', 't')]

If you can, always pass a :class:`~corpy.morphodita.Tagger` to
:func:`~corpy.phonetics.cs.transcribe` (see :doc:`morphodita` on where to
download tagger models). The function will use it to attempt to be smarter about
the pronunciation of words based on their morphemic structure. For instance,
without a tagger, both *neuron* and *neurozený* will have a diphthong:

.. code:: python

   >>> cs.transcribe("neuron")
   [('n', 'E_u', 'r', 'o', 'n')]
   >>> cs.transcribe("neurozený")
   [('n', 'E_u', 'r', 'o', 'z', 'E', 'n', 'i:')]

With a tagger, the *ne-* in *neurozený* will be identified as a prefix and
*-eu-* will therefore be correctly rendered as a two-vowel sequence:

.. code:: python

   >>> from corpy.morphodita import Tagger
   >>> tagger = Tagger("./czech-morfflex-pdt.tagger")
   >>> cs.transcribe("neurozený", tagger=tagger)
   [('n', 'E', 'u', 'r', 'o', 'z', 'E', 'n', 'i:')]

While *neuron* will correctly retain its diphthong:

.. code:: python

   >>> cs.transcribe("neuron", tagger=tagger)
   [('n', 'E_u', 'r', 'o', 'n')]

Hyphens can be used to manually prevent interactions between neighboring phones,
e.g. prevent assimilation of voicing:

.. code:: python

   >>> cs.transcribe("máš -hlad")
   [('m', 'a:', 'S'), ('h\\', 'l', 'a', 't')]

Or prevent adjacent vowels from merging into a diphthong, even without a tagger:

.. code:: python

   >>> cs.transcribe("ne-urozený")
   [('n', 'E', 'u', 'r', 'o', 'z', 'E', 'n', 'i:')]

As you can see, these special hyphens get deleted in the process of
transcription, so if you want a literal hyphen, it must be inside a token with
either no alphabetic characters, or at least one other non-alphabetic character:

.. code:: python

   >>> cs.transcribe("- --- -.- -hlad?")
   ['-', '---', '-.-', '-hlad?']

In general, tokens containing non-alphabetic characters (modulo the special
treatment of hyphens described above) are passed through as is:

.. code:: python

   >>> cs.transcribe("máš ? hlad")
   [('m', 'a:', 'Z'), '?', ('h\\', 'l', 'a', 't')]

And you can even configure some of them to constitute a blocking boundary for
interactions between phones (notice that unlike in the previous example, "máš"
ends with a /S/ → assimilation of voicing wasn't allowed to spread past the
".."):

.. code:: python

   >>> cs.transcribe("máš .. hlad", prosodic_boundary_symbols={".."})
   [('m', 'a:', 'S'), '..', ('h\\', 'l', 'a', 't')]

Finally, when the input is a single string, it's simply split on whitespace, but
you can also provide your own tokenization. E.g. if your input string contains
unspaced square brackets to mark overlapping speech, this is probably not the
output you want:

.. code:: python

   >>> cs.transcribe("[máš] hlad")
   ['[máš]', ('h\\', 'l', 'a', 't')]

But if you pretokenize the input yourself according to rules that make sense in
your situation, you're good to go:

.. code:: python

   >>> cs.transcribe(["[", "máš", "]", "hlad"])
   ['[', ('m', 'a:', 'Z'), ']', ('h\\', 'l', 'a', 't')]

Acknowledgments
===============

The choice of (X-)SAMPA and IPA transcription symbols follows the `guidelines
<https://fonetika.ff.cuni.cz/o-fonetice/foneticka-transkripce/czech-sampa/>`_
published by the Institute of Phonetics, Faculty of Arts, Charles University,
Prague, which are hereby gratefully acknowledged.
