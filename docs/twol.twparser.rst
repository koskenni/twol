twol\.twparser module
=====================

This module interfaces the syntactic parsing by TatSu with the formulas which convert the expressions to FSTs or equivalent for composing the expressions from which the two-level rules are compiled.

The module contains one set of formulas for compiling the elementary exprssions directly to FSTs and then combining them with FST operations into larger units.  The other set combines just XFST strings which would be compiled as XFST regular expressions into FSTs.  That line of processing may or may not be still operational.  Any way, it has not been tested for a while.

The ``twparser`` module needs the TatSu package and the EBNF syntax file ``twolcsyntax.ebnf`` whicdefines the formal syntax of the two-level rule formalis.  It comes with the ``twol`` package.

.. automodule:: twol.twparser
    :members:
    :undoc-members:
    :show-inheritance:
