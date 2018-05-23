=====
CorPy
=====

What is CorPy?
==============

A fancy plural for *corpus* ;) Also, a collection of handy but not especially
mutually integrated tools for dealing with linguistic data. It abstracts away
functionality which is often needed in practice in day to day work at the
`Czech National Corpus <https://korpus.cz>`_, without aspiring to be a fully
featured or consistent NLP framework.

Currently available sub-packages are:

- `morphodita <corpy/morphodita/README.rst>`_: tokenizing and tagging raw
  textual data using `MorphoDiTa <https://github.com/ufal/morphodita>`_
- `vertical <corpy/vertical/README.rst>`_: parsing corpora in the vertical
  format devised originally for `CWB <http://cwb.sourceforge.net/>`_, used also
  by `(No)SketchEngine <https://nlp.fi.muni.cz/trac/noske/>`_
- `phonetics <corpy/phonetics/README.rst>`_: rule-based phonetic transcription
  of Czech

Installation
============

.. code:: bash

   $ pip3 install git+https://github.com/dlukes/corpy

Requirements
============

Only recent versions of Python 3 are supported by design.

License
=======

Copyright © 2016--present `ÚČNK <http://korpus.cz>`_/David Lukeš

Distributed under the `GNU General Public License v3
<http://www.gnu.org/licenses/gpl-3.0.en.html>`_.
