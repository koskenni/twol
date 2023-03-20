twol\.twparser module
=====================

See also  :ref:`pytwol-glossary` and [karttunen1987]_.

Parsing the two-level rules
---------------------------

The rules and the definitons are parsed by using a parser generator called TatSu by by Juancarlo Añez which is available in Github.  The syntax of the regular expressions, definitions and rules was defined by using an Extended BNF formalism of TatSu as a file `twolcsyntax.ebnf <https://github.com/koskenni/twol/raw/master/twol/twolsyntax.ebnf>`__.  TatSu offers several types of semantics to be used.  The one that is presently used compiles the regular expressions directly to FSTs. Another option that was tried earlier was to let the syntax productions return strings in the XFST regular expression formalism, and compile the string as a regular expression when it is a complete expression.  See  http://tatsu.readthedocs.io/en/stable/index.html for the documentation of TatSu.

The parsing is done one definition or a rule at a time.  The main result of a definition is the defined expresssion as a FST which is saved for rules and further definitions.  If the name of the definition occurs there, the saved FST is used as the value.  The result when a rule is parsed a tuple which indicates what type it is and a collection of FSTs which correspond to the components of the rule.  The parser generator provides error diagnostics (by using Python exceptions).  The location of the error in the input line is usually correctly recognized and reported to the user.

The semantics in ``twol.twparser`` does some additional checks including the test that the input symbols, the output symbols and the pair symbols used in the rules actually occur in the examples.  Therefore, the example file must be already processed by ``twol.twexamp`` before this module is used.  The set of allowed symbols and symbol pairs is needed for checking the correctness of the rules and also in the compiliing of the component expressions into FSTs.

This module interfaces the syntactic parsing by TatSu with the formulas which convert the expressions to FSTs or equivalent for composing the expressions from which the two-level rules are compiled.

The module contains one set of formulas for compiling the elementary expressions directly to FSTs and then combining them with FST operations into larger units.  The other set combines just XFST strings which would be compiled as XFST regular expressions into FSTs.  That line of processing may or may not be still operational.  Anyway, it has not been tested for a while.

The ``twol.twparser`` module needs the TatSu package and the EBNF syntax file ``twolcsyntax.ebnf`` whicdefines the formal syntax of the two-level rule formalism.  The EBNF file is part of the ``twol`` package.

.. automodule:: twol.twparser
    :members:
    :undoc-members:
    :show-inheritance:
