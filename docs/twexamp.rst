=======
twexamp
=======

The ``twexamp.py`` module can also be used as a standalone script or command in order to convert examples in *pair string* format into a :term:`finite-state transducer` (FST).  Examples in pair string format are plain human readable text files, one example per line, where each example is give as a space-separated sequence of pair symbols, e.g.::

  k a u p {pØ}:Ø {ao}:a s s {aä}:a

The invocation of the program could be e.g.::

  $ python3 twexamp.py examples.pstr examples.fst


Functions of the ``twexamp`` module
===================================

.. automodule:: twexamp
   :members:
