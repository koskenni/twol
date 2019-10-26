.. warning:: This document is under construction


===================================================
TWOL rules with Python regular expression semantics
===================================================

The two-level rules can be parsed according to a grammar written in Extended Backus Naur Form (EBNF).  In order to compile the rules into some usable form, a semantic interpretation has to be attached to the productions.  The present solution in twol.py is to compile the components into FSTs right from the beginning and combine the FSTs in productions using HFST operations.  The context and other components are compiled this way until they are compiled into the rule transducers.  In order to use the compiled rules effectively, they have to be converted into FSTs.

On the other hand, one can convert the two-level rules into XFST regular expressions until they represent the expressions out of which the contexts and centers of the rule are made.  These XFST expressions can, then, be compiled and the final rules compiled out of them.  This approach was used earlier in the twol.py program.

There is another possibility, discussed in this article, to compile the two-level rules to Python regular expressions.  Rules so compiled would not be practical for analyzing large amounts of texts.  Instead, such an approach would be quite practical for writing and testing two-level rules.


Representing partial expressions
================================

A ``symbol_or_pair`` is always one symbol long and, therefore, it could be expressed either as a string or as a set of symbol pairs, and the same goes for other expressions of length one:

========== =============== ===========================
token      RE string       Python set
========== =============== ===========================
x          x               {(x,x)}
x:y        x:y             {(x,y)}
:y         [^ ]+:y         pairs_for_output(y)
x:         x:[^ ]+         pairs_for_input(x)
:          [^ ]+:[^ ]+     all_pairs_set
X Y        X Y             None
X & Y      None            X&Y or X.intersection(Y)
X | Y      X|Y             None
\\X        None            all_pairs_set - X
X .o. Y    None            pair_compose(X, Y) 
                           & all_pairs_set
X - Y      None            X-Y or X.difference(Y)
X.u        None            set([(x,x) for x,y in X])
X.l        None            set([(y,y) for x,y in X])
========== =============== ===========================

As long as there is a set representation (i.e. all sequences the expression represents are one symbol pair long), one can go on using the set representation in many operations (except '*', '+' and concatenation).  When combining nodes during the parsing, both the RE and the set representations are built, if possible.  At some points we may lose the RE and then we keep the set representation.  At other points we may lose the set representation and then we must convert it to a string representation.  In addition, a pair_compose() function must be written.


Using RE two-level rules
========================

The parser with its semantic rules can produce a tuple which is sufficient for making the rules operational::

  (operator, x_part, context_lst)

The rule interpreter can use the x_part to identify relevant examples for the rule and to locate the interesting positions in them.

Testing positive examples
=========================

Each such position can then be tested against the list of context.  Each context is checked just by matching the left context regular expression against the string that precedes the occurrence and the right context in the same way.  If both match successfully, then the context condition is met.  If none of the contexts succeed, the rule fails.  This kind of checking appears to provide at least as good diagnostic information as the traditional approach where rules are compiled into FSTs.

Creating negative examples
==========================

See ...
