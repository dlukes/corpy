=====
CorPy
=====

What is CorPy?
==============

A fancy plural for *corpus* ;) Also, a collection of handy but not especially
mutually integrated tools for dealing with linguistic data. It abstracts away
functionality which is often needed in practice in day to day work at the
`Czech National Corpus <https://korpus.cz>`__, without aspiring to be a fully
featured or consistent NLP framework.

Currently available sub-packages are:

- `morphodita <corpy/morphodita/README.rst>`__: tokenizing and tagging raw
  textual data using `MorphoDiTa <https://github.com/ufal/morphodita>`__
- `vertical <corpy/vertical/README.rst>`__: parsing corpora in the vertical
  format devised originally for `CWB <http://cwb.sourceforge.net/>`__, used also
  by `(No)SketchEngine <https://nlp.fi.muni.cz/trac/noske/>`__
- `phonetics <corpy/phonetics/README.rst>`__: rule-based phonetic transcription
  of Czech

Installation
============

.. code:: bash

   $ pip3 install corpy

Requirements
============

Only recent versions of Python 3 are supported by design.

License
=======

Copyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš

Distributed under the `GNU General Public License v3
<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.
