.. _discover:

twol\.discover module
=====================

Sets of positive and negative contexts
--------------------------------------

The discovery processes one :term:`pair symbol`.  If all pair symbols for a :term:`morphophoneme` are to be processed, it is done separately for each pair symbol.  For the pair, e.g. ``{tds}:s``, the set of relevant :term:`contexts <context>` is first extracted out of the whole set of examples.  The relevant contexsts consist of (1) the positive contexts (``positive_contexts``) where the pair (e.g. ``{tds}:s``) occurs and (2) negative contexts (``negative_contexts``) where the morphophoneme of the pair occurs but with any other surface phoneme (e.g. ``{tds}:t`` or ``{tds}:d``).  If any contexts in the negative set would occur in the positive set, such contexts are removed from the negative set.  Each context in those sets consists of a pair of two strings: the left context and the right context.

In this module, examples are treated as strings of space-separated pair symbols, e.g.::

  "k ä {tds}:s {ieØeØ}:i"
  "k ä {tds}:d {ieØeØ}:e n"

Thus one element in the set of positive context pairs for ``{tds}:s`` would be::

  (".#. k ä", "{ieØeØ}:i .#.")

Note the symbol ``.#.`` which denotes the end of the left or right context.   The set of negative context context pairs for ``{tds}:s`` could include the following pair::

  (".#. k ä", "{ieØeØ}:e n .#.")


The sets of positive and the negative contexts afe built and the positive is subtracted from the negative.  The negative contexts remain constant during the processing whereas the positive ones are modified by truncations and/or substitutions.  


Generalising the sets of contexts
---------------------------------

These initial sets of contexts correspond to the trivial rule which constrains the occurrence of the pair symbol within the set of examples.  Such a rule is correct but does not work outside the set of examples because the contexts are too restrictive.  The task of the discovery procedure is to generalise the positive and the negative sets while keeping the two sets mutually exclusive.

The program modifies the positive context sets but keeps the negative sets constant.  Therefore, the comparisons between positive and negative context sets is performed with functions which correctly deduce the inclusions or disjointness.

Python functions of the module
------------------------------

.. automodule:: twol.discover
    :members:
    :undoc-members:
    :show-inheritance:
