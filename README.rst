=====
CorPy
=====

.. image:: https://readthedocs.org/projects/corpy/badge/?version=stable
   :target: https://corpy.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation status

.. image:: https://badge.fury.io/py/corpy.svg
   :target: https://badge.fury.io/py/corpy
   :alt: PyPI package

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
   :alt: Code style

What is CorPy?
==============

A fancy plural for *corpus* ;) Also, a collection of handy but not especially
mutually integrated tools for dealing with linguistic data. It abstracts away
functionality which is often needed in practice for teaching and/or day to day
work at the `Czech National Corpus <https://korpus.cz>`__, without aspiring to
be a fully featured or consistent NLP framework.

The short URL to the docs is: https://corpy.rtfd.io/

Here's an idea of what you can do with CorPy:

- add linguistic annotation to raw textual data using either UDPipe_ or
  MorphoDiTa_

.. _UDPipe: http://ufal.mff.cuni.cz/udpipe
.. _MorphoDiTa: http://ufal.mff.cuni.cz/morphodita

.. note::

   **Should I pick UDPipe or MorphoDiTa?**

   UDPipe_ is the successor to MorphoDiTa_, extending and improving upon the
   original codebase. It has more features at the cost of being somewhat more
   complex: it does both `morphological tagging (including lemmatization) and
   syntactic parsing <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__,
   and it handles a number of different input and output formats. You can also
   download `pre-trained models <http://ufal.mff.cuni.cz/udpipe/models>`__ for
   many different languages.

   By contrast, MorphoDiTa_ only has `pre-trained models for Czech and English
   <http://ufal.mff.cuni.cz/morphodita/users-manual>`__, and only performs
   `morphological tagging (including lemmatization)
   <https://corpy.rtfd.io/en/stable/guides/morphodita.html>`__. However, its
   output is more straightforward -- it just splits your text into tokens and
   annotates them, whereas UDPipe can (depending on the model) introduce
   additional tokens necessary for a more explicit analysis, add multi-word
   tokens etc. This is because UDPipe is tailored to the type of linguistic
   analysis conducted within the UniversalDependencies_ project, using the
   CoNLL-U_ data format.

   MorphoDiTa can also help you if you just want to tokenize text and don't have
   a language model available.

.. _UniversalDependencies: https://universaldependencies.org
.. _CoNLL-U: https://universaldependencies.org/format.html

- `easily generate word clouds
  <https://corpy.rtfd.io/en/stable/guides/vis.html>`__
- `generate phonetic transcripts of Czech texts
  <https://corpy.rtfd.io/en/stable/guides/phonetics_cs.html>`__
- `wrangle corpora in the vertical format
  <https://corpy.rtfd.io/en/stable/guides/vertical.html>`__ devised originally
  for `CWB <http://cwb.sourceforge.net/>`__, used also by `(No)SketchEngine
  <https://nlp.fi.muni.cz/trac/noske/>`__
- plus some `command line utilities
  <https://corpy.rtfd.io/en/stable/guides/cli.html>`__

Installation
============

.. code:: bash

   $ pip3 install corpy

Requirements
============

Only recent versions of Python 3 (3.6+) are supported by design.

Development
===========

Dependencies and building the docs
----------------------------------

The canonical dependency requirements are listed in ``pyproject.toml`` and
frozen in ``poetry.lock``. However, in order to use ``autodoc`` to build the API
docs, the package has to be installed, and ``corpy`` has dependencies that are
too resource-intensive to build on ReadTheDocs.

The solution is to use a dummy ``setup.py`` which lists *only* the dependencies
needed to build the docs properly, and mock all other dependencies by listing
them in ``autodoc_mock_imports`` in ``docs/conf.py``. This dummy ``setup.py`` is
used to install ``corpy`` *only* on ReadTheDocs (via the appropriate config
option in ``.readthedocs.yml``). The same goes for the ``MANIFEST.in`` file,
which duplicates the ``tool.poetry.include`` entries in ``pyproject.toml`` for
the sole benefit of ReadTheDocs.

.. license-marker

License
=======

Copyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš

Distributed under the `GNU General Public License v3
<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.
