.. _twrule: 


twol\.twrule module
===================

This module forms the rule FSTs out of the collection of component FSTs which have been compiled by ``twol.twparse`` out of the center parts, left and right contexts of the rules.

Compiling the two-level rules
-----------------------------

The actual compilation starts from the tuples which contain the components as FSTs.  Each rule is parsed and compiled separately using the alphabet extracted from the FST containing the examples.  The method for the compilation is described in [ylijyrä2006]_. The main result of the compilation is the rule FST but two other FSTs are compiled in addition:

- *rule_fst* which accepts any examples which conform to the rule.  The *rule_fst* accepts strings of symbol pairs.  A rule FST ought to accept all symbol pair strings where the X part occurs in one of the contexts in the rule and/or reject thse strings where this is not the case.

- *selector_fst* produces the relevant subset of the examples when intersected with *examples_fst*.  The selector is needed only for testing that the rule accepts all relevant positive examples.  The point is that not all examples are relevant for testing.  If an example does not contain the center (or the input part of the center) of a rule, the rule accepts such an example anyway.  The function ``selector_from_x(X)`` builds this simply by concatenating ``PI* X PI*``. 

- *scrambler_fsa* which is an encoded FSA which transforms a positive example into a negative example which ought to be rejected by the rule (and is also needed only for the testing of the rule).  The purpose of scrambling is to alter the output symbol in order to produce occurrences in wrong places for right-arrow rules or wrong correspondences in a context for left-arrow rules.


Compilation of the rule FST
---------------------------

There is a separate function for each type of rules: ``rightarrow()`` for ``=>`` rules, ``output_coercion()`` for ``<=`` rules, ``input_coercion()`` for the new ``<---`` type of rules, ``doublearrow()`` for ``<=>`` rules, and ``center_exclusion()`` for ``/<=`` rules.  The rule FSTs are compiled using the :term:`generalized restriction` method in [ylijyrä2006]_.

The rule formalism has a special symbol ``.#.`` for the beginning of the left context or the end of the right context.  The compilation makes some effort to implement this literally so that the FSTs do not have transitions for stuff beyond the boundary symbol.  The parser inserts ``BEGIN`` for a left context boundary and ``END`` symbol in the right context.  Function ``begin_end()`` takes care of the cleaning the FSTs.


Constructing the scrambler_fsa
------------------------------

Let us suppose we have a rule: ``{ao}:o => _ {ij}: ;``  and an example::

  k a l {ao}:a s s {aä}:a

In order to produce negative examples for this rules, we have to change occurrences of ``{ao}:o`` into ``{ao}:a`` at least in one place of an example, e.g.::

  k a l {ao}:o s s {aä}:a

In order to make such changes, the original examples are encoded as FSAs where the original input and output symbols are separated by a '``^``'::

  k^k a^a l^l {ao}^a s^s s^s {aä}^a

Such sequences can be converted with appropriate FSTs if its input symbols are pairs (such as ``k^k`` or ``{ao}^a``).  In order not to lose information, the output symbols have to be similar pairs.

Functions of the module
-----------------------

.. automodule:: twol.twrule
    :members:
    :undoc-members:
    :show-inheritance:
