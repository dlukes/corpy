======================================
Wrangle corpora in the vertical format
======================================

Overview
========

Tools for parsing corpora in the vertical format devised originally for `CWB
<http://cwb.sourceforge.net/>`_, used also by `(No)SketchEngine
<https://nlp.fi.muni.cz/trac/noske/>`_. It would have been nice if verticals
were just standards compliant XML, but they appeared before XML, so they're
not. Hence this.

NOTE: The examples below are currently not tested because they require the
:file:`syn2015.gz` vertical file to be available, which is large and should not
be freely distributed.

.. code:: python

   >>> import pytest
   >>> pytest.skip("examples not tested")

Iterating over positions in a vertical file
===========================================

This allows you to iterate over all positions while keeping track of the
structural attributes of the structures they're contained within, without
risking errors from hand-coding this logic every time you need it.

.. code:: python

   >>> from corpy.vertical import Syn2015Vertical
   >>> from pprint import pprint
   >>> v = Syn2015Vertical("path/to/syn2015.gz")
   >>> for i, position in enumerate(v.positions()):
   ...     if i % 100 == 0:
   ...         # structural attributes of position
   ...         pprint(v.sattrs)
   ...         print()
   ...         # position itself
   ...         pprint(position)
   ...         print()
   ...     elif i > 100:
   ...         break
   ...
   {'doc': {'audience': 'GEN: obecné publikum',
           'author': 'Typlt, Jaromír',
           'authsex': 'M: muž',
           'biblio': 'Typlt, Jaromír (1993): Zápas s rodokmenem. Praha: Pražská '
                     'imaginace.',
           'first_published': '1993',
           'genre': 'X: neuvedeno',
           'genre_group': 'X: neuvedeno',
           'id': 'pi291',
           'isbnissn': '80-7110-132-X',
           'issue': '',
           'medium': 'B: kniha',
           'periodicity': 'NP: neperiodická publikace',
           'publisher': 'Pražská imaginace',
           'pubplace': 'Praha',
           'pubyear': '1993',
           'srclang': 'cs: čeština',
           'subtitle': 'Groteskní mýtus',
           'title': 'Zápas s rodokmenem',
           'translator': 'X',
           'transsex': 'X: neuvedeno',
           'txtype': 'NOV: próza',
           'txtype_group': 'FIC: beletrie'},
   'p': {'id': 'pi291:1:1', 'type': 'normal'},
   's': {'id': 'pi291:1:1:1'},
   'text': {'author': '', 'id': 'pi291:1', 'section': '', 'section_orig': ''}}

   Position(word='ZÁPAS', lemma='zápas', tag=UtklTag(pos='N', sub='N', gen='I', num='S', case='1', pgen='-', pnum='-', pers='-', tense='-', grad='-', neg='A', act='-', p13='-', p14='-', var='-', asp='-'), proc='T', afun='ExD', parent='0', eparent='0', prep='', p_lemma='', p_tag='', p_afun='', ep_lemma='', ep_tag='', ep_afun='')

   {'doc': {'audience': 'GEN: obecné publikum',
           'author': 'Typlt, Jaromír',
           'authsex': 'M: muž',
           'biblio': 'Typlt, Jaromír (1993): Zápas s rodokmenem. Praha: Pražská '
                     'imaginace.',
           'first_published': '1993',
           'genre': 'X: neuvedeno',
           'genre_group': 'X: neuvedeno',
           'id': 'pi291',
           'isbnissn': '80-7110-132-X',
           'issue': '',
           'medium': 'B: kniha',
           'periodicity': 'NP: neperiodická publikace',
           'publisher': 'Pražská imaginace',
           'pubplace': 'Praha',
           'pubyear': '1993',
           'srclang': 'cs: čeština',
           'subtitle': 'Groteskní mýtus',
           'title': 'Zápas s rodokmenem',
           'translator': 'X',
           'transsex': 'X: neuvedeno',
           'txtype': 'NOV: próza',
           'txtype_group': 'FIC: beletrie'},
   'p': {'id': 'pi291:1:3', 'type': 'normal'},
   's': {'id': 'pi291:1:3:2'},
   'text': {'author': '', 'id': 'pi291:1', 'section': '', 'section_orig': ''}}

   Position(word='chvil', lemma='chvíle', tag=UtklTag(pos='N', sub='N', gen='F', num='P', case='2', pgen='-', pnum='-', pers='-', tense='-', grad='-', neg='A', act='-', p13='-', p14='-', var='-', asp='-'), proc='M', afun='Atr', parent='-1', eparent='-1', prep='', p_lemma='několik', p_tag='Ca--4-----------', p_afun='Adv', ep_lemma='několik', ep_tag='Ca--4-----------', ep_afun='Adv')

Performing frequency distribution queries
=========================================

This can be done elegantly and fairly quickly with
:meth:`~corpy.vertical.Vertical.search`. All you have to do is provide a match
function, which identifies positions which the query should match, and a count
function, which specifies what should be counted for each match.

The return value is an index of occurrences and the total size of the corpus.
The index is a dictionary of numpy array of position indices within the corpus,
which can be further processed e.g. using :func:`~corpy.vertical.ipm` or
:func:`~corpy.vertical.arf` to compute different types of frequencies.

.. code:: python

   >>> from corpy.vertical import Syn2015Vertical, ipm, arf
   >>> v = Syn2015Vertical("path/to/syn2015.gz")
   # log progress every 50M positions
   >>> v.report = 50_000_000
   >>> def match(posattrs, sattrs):
   ...     # match all nouns within txtype_group "FIC: beletrie"
   ...     return sattrs["doc"]["txtype_group"] == "FIC: beletrie" and posattrs.tag.pos == "N"
   ...
   >>> def count(posattrs, sattrs):
   ...     # at each matched position, record the txtype and lemma
   ...     return sattrs["doc"]["txtype"], posattrs.lemma
   ...
   >>> index, N = v.search(match, count)
   Processed 0 lines in 0:00:00.007382.
   Processed 50,000,000 lines in 0:05:58.185566.
   Processed 100,000,000 lines in 0:11:35.394294.

**NOTE:** this was run on a desktop workstation, with the data being stored on
a networked filesystem. If the performance of any future versions on a similar
task becomes significantly worse than this ballpark, it should be considered a
bug.

.. code:: python

   # absolute frequency
   >>> len(index[("NOV: próza", "plíseň")])
   211
   # relative frequency (instances per million)
   >>> ipm(index[("NOV: próza", "plíseň")], N)
   1.747430618598555
   # average reduced frequency (takes into account dispersion)
   >>> arf(index[("NOV: próza", "plíseň")], N)
   54.220727998809153

Subclass :class:`~corpy.vertical.Vertical` for your custom corpus
=================================================================

If you have a corpus with a different structure, you can easily adapt the tools
by subclassing :class:`~corpy.vertical.Vertical`. See its docstring for further
info, or the implementation of :class:`~corpy.vertical.Syn2015Vertical` for a
practical example.
