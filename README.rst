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

Installation
============

.. code:: bash

   $ python3 -m pip install corpy

Only recent versions of Python 3 (3.7+) are supported by design.

Help and feedback
=================

If you get stuck, it's always a good idea to start by searching the
documentation, the short URL to which is https://corpy.rtfd.io/.

The project is developed on GitHub_. You can ask for help via `GitHub
discussions`_ and report bugs and give other kinds of feedback via `GitHub
issues`_. Support is provided gladly, time and other engagements permitting, but
cannot be guaranteed.

.. _GitHub: https://github.com/dlukes/corpy
.. _GitHub discussions: https://github.com/dlukes/corpy/discussions
.. _GitHub issues: https://github.com/dlukes/corpy/issues

What is CorPy?
==============

A fancy plural for *corpus* ;) Also, a collection of handy but not especially
mutually integrated tools for dealing with linguistic data. It abstracts away
functionality which is often needed in practice for teaching and/or day to day
work at the `Czech National Corpus <https://korpus.cz>`__, without aspiring to
be a fully featured or consistent NLP framework.

Here's an idea of what you can do with CorPy:

- add linguistic annotation to raw textual data using either `UDPipe
  <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__ or `MorphoDiTa
  <https://corpy.rtfd.io/en/stable/guides/morphodita.html>`__
- `easily generate word clouds
  <https://corpy.rtfd.io/en/stable/guides/vis.html>`__
- `generate phonetic transcripts of Czech texts
  <https://corpy.rtfd.io/en/stable/guides/phonetics_cs.html>`__
- `wrangle corpora in the vertical format
  <https://corpy.rtfd.io/en/stable/guides/vertical.html>`__ devised originally
  for `CWB <http://cwb.sourceforge.net/>`__, used also by `(No)SketchEngine
  <https://nlp.fi.muni.cz/trac/noske/>`__
- plus some utilities for `interactive Python coding
  <https://corpy.rtfd.io/en/stable/guides/util.html>`__ (e.g. with Jupyter
  notebooks in  `JupyterLab <https://jupyterlab.rtfd.io>`__) and the `command
  line <https://corpy.rtfd.io/en/stable/guides/cli.html>`__

.. note::

   **Should I pick UDPipe or MorphoDiTa?**

   Both are developed at `ÚFAL MFF UK`_. UDPipe_ has more features at the cost
   of being somewhat more complex: it does both `morphological tagging
   (including lemmatization) and syntactic parsing
   <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__, and it handles a
   number of different input and output formats. You can also download
   `pre-trained models <http://ufal.mff.cuni.cz/udpipe/models>`__ for many
   different languages.

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

.. _`ÚFAL MFF UK`: https://ufal.mff.cuni.cz/
.. _UDPipe: https://ufal.mff.cuni.cz/udpipe
.. _MorphoDiTa: https://ufal.mff.cuni.cz/morphodita
.. _UniversalDependencies: https://universaldependencies.org
.. _CoNLL-U: https://universaldependencies.org/format.html

.. development-marker

Development
===========

Dependencies and building the docs
----------------------------------

``corpy`` needs to be installed in the ReadTheDocs virtualenv for ``autodoc`` to
work. That's configured in ``.readthedocs.yml``. However, ``pip`` doesn't
install ``[tool.poetry.dev-dependencies]``, which contain the Sphinx version and
theme we're using. Maybe there's a way of forcing that, but we probably don't
want to anyway -- it's a waste of time to install linters, testing frameworks
etc. that won't be used. So instead, we have a ``docs/requirements.txt`` file
managed by ``check.sh`` which only contains Sphinx + the theme, and which we
specify via ``.readthedocs.yml``.

.. license-marker

License
=======

Copyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš

Distributed under the `GNU General Public License v3
<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.
