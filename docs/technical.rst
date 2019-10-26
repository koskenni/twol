========================================================
Technical details about the rule compilation and testing
========================================================

See also  :ref:`pytwol-glossary` and [karttunen1987]_.

---------------------------
Parsing the two-level rules
---------------------------

The rules and the definitons are parsed by using a parser generator called TATSU by by Juancarlo Añez which is available in Github.  The syntax of the regular expressions, definitions and rules was defined by using an extended BNF formalism of TATSU as a file ``twolcsyntax.ebnf``.  TATSU offers several types of semantics to be used.  The one that is presently used compiles the regular expressions directly to FSTs. Another option that was tried earlier was to let the syntax productions return strings in the XFST regular expression formalism, and compile the string as a regular expression when it is a complete expression.  See  http://tatsu.readthedocs.io/en/stable/index.html for the documentation of TATSU.

The parsing is done one definition or a rule at a time.  The main result of a definition is the defined expresssion as a FST which is saved for further definitions and rules.  If the name of the definition occurs there, the saved FST is used as the value.  The result when a rule is parsed a tuple which indicates what type it is and a collection of FSTs which correspond to the components of the rule.  The parser generator provides error diagnostics (by using Python exceptions).  The location of the error in the input line is usually correctly recognized and reported to the user.  The semantics in ``twparser.py`` does some additional checks including the test that the input symbols, the output symbols and the pair symbols used in the rules actually occur in the examples.

-----------------------------
Compiling the two-level rules
-----------------------------

The actual compilation starts from the tuples which contain the components as FSTs.  Each rule is compiled separately using the alphabet extracted from the FST containing the examples.  The method for the compilation is described in [ylijyrä2006]_. The main result of the compilation is the rule FST but two other FSTs are compiled in addition:

- *rule_fst* which accepts any examples which conform to the rule.  The *rule_fst* accepts strings of symbol pairs.  A rule FST ought to accept all symbol pair strings where the X part occurs in one of the contexts in the rule and/or reject thse strings where this is not the case.

- *selector_fst* produces the relevant subset of the examples when intersected with *examples_fst*.  The selector is needed only for testing that the rule accepts all relevant positive examples.  The point is that not all examples are relevant for testing.  If an example does not contain the center (or the input part of the center) of a rule, the rule accepts such an example anyway. 

- *scrambler_fsa* which is an encoded FSA which transforms a positive example into a negative example which ought to be rejected by the rule (and is also needed only for the testing of the rule).  The purpose of scrambling is to alter the output symbol in order to produce occurrences in wrong places for right-arrow rules or wrong correspondences in a context for left-arrow rules.

Compilation of the rule FST
===========================

Constructing the selector_fst
=============================

Constructing the scrambler_fsa
==============================

Let us suppose we have a rule: ``{ao}:o => _ {ij}: ;``  and an example::

  k a l {ao}:a s s {aä}:a

In order to produce negative examples for this rules, we have to change occurrences of ``{ao}:o`` into ``{ao}:a`` at least in one place of an example, e.g.::

  k a l {ao}:o s s {aä}:a

In order to make such changes, the original examples are encoded as FSAs where the original input and output symbols are separated by a '``^``'::

  k^k a^a l^l {ao}^a s^s s^s {aä}^a

Such sequences can be converted with appropriate FSTs if its input symbols are pairs (such as ``k^k`` or ``{ao}^a``).  In order not to lose information, the output symbols have to be similar pairs.

