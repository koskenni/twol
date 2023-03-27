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


The sets of positive and the negative contexts afe built and the positive is subtracted from the negative.

Generalising the sets of contexts
---------------------------------

These initial sets of contexts correspond to the trivial rule which constrains the occurrence of the pair symbol within the set of examples.  Such a rule is correct but does not work outside the set of examples because the contexts are too restrictive.  The task of the discovery procedure is to generalise the positive and the negative sets while keeping the two sets mutually exclusive.

One way to generalise the contest is to replace a set of pair symbols with a new symbol, such as symbols ``{ij}:i``, ``{ieØeØ}:i``, ``{V}:i`` and ``i`` with ``:i``.  The replacement is feasible if after applying it, the positive set and the negative set remain disjoint.  A possible reduction worth testing could be to reduce all pairs ``x:x`` to ``:x``.

Another way to generalise the contexts is to shorten them.  One can set a maximum length to the left contexts.  If the  set of truncated positive contexs is still disjoint from the corresponding set of negative contexts, then the new sets can replace the original sets.  One can then proceed with potential further left truncations or right truncations.

A rule corresponding truncated contexts clearly accepts all positive examples but if the truncation is too heavy, some negative examples will accepted along with the correct ones.

The generalising pair symbols might be done first and the truncation then or the other way round.  The order might affect what the final result of the discovery procedure will be (and some experiments are needed).

During the steps of the reduction, the sets of positive and negative examples are treated as steps.  If the recuction produces an identical context out of two or more earlier contexts, then the resulting set is smaller -- and this is of, course a good sign as we are looking for a compact and general expression for the rule.


Python functions of the module
------------------------------

.. automodule:: twol.discover
    :members:
    :undoc-members:
    :show-inheritance:
