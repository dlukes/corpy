=====
CorPy
=====

.. image:: https://readthedocs.org/projects/corpy/badge/?version=latest
   :target: https://corpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation status

.. image:: https://badge.fury.io/py/corpy.svg
   :target: https://badge.fury.io/py/corpy
   :alt: PyPI package

What is CorPy?
==============

A fancy plural for *corpus* ;) Also, a collection of handy but not especially
mutually integrated tools for dealing with linguistic data. It abstracts away
functionality which is often needed in practice for teaching and/or day to day
work at the `Czech National Corpus <https://korpus.cz>`__, without aspiring to
be a fully featured or consistent NLP framework.

The short URL to the docs is: https://corpy.rtfd.io/

Here's an idea of what you can do with CorPy:

- `tokenize and morphologically tag
  <https://corpy.rtfd.io/en/latest/guides/morphodita.html>`__ raw textual data
  using `MorphoDiTa <https://github.com/ufal/morphodita>`__
- `easily generate word clouds
  <https://corpy.rtfd.io/en/latest/guides/vis.html>`__
- `generate phonetic transcripts of Czech texts
  <https://corpy.rtfd.io/en/latest/guides/phonetics_cs.html>`__
- `wrangle corpora in the vertical format
  <https://corpy.rtfd.io/en/latest/guides/vertical.html>`__ devised originally
  for `CWB <http://cwb.sourceforge.net/>`__, used also by `(No)SketchEngine
  <https://nlp.fi.muni.cz/trac/noske/>`__
- plus some `command line utilities
  <https://corpy.rtfd.io/en/latest/guides/cli.html>`__

Installation
============

.. code:: bash

   $ pip3 install corpy

Requirements
============

Only recent versions of Python 3 (3.6+) are supported by design.

.. license-marker

License
=======

Copyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš

Distributed under the `GNU General Public License v3
<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.
