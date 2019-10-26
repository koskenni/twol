.. _differences:

==========================================
Differences between twol.py and hfst-twolc
==========================================

.. index:: HFST, hfst-twolc
   pair: rule; compiler

The simplified two-level morphology differs in several respects from the standard model as described in publications and as implemented in the TWOLC compiler by Karttunen and Beesley and later on in the HFST finite-state transducer tools, see e.g.  [karttunen1987]_.  There are changes in the formalism (i.e. syntax of expressions and rules) and there are some strongly recommended practises which the author of the rules are expected to follow:

.. index:: alphabet

1. The simplified model bases heavily on *examples*.  No rules can be written without a set of examples.  The examples are given as a sequences of of :term:`pair symbols <pair symbol>` such as::
     
     k a u p {pØ}:Ø {ao}:a s s {aä}:a

   The alphabet (morphophonemes or input symbols, surface phonemes or output symbols and the set of allowed symbol pairs) is deduced from the examples.  The twol.py compiler neither needs nor accepts alphabet or character set definitions.  A set of examples needs to be converted into a FST before the compilation, see :doc:`twexamp`.

2. In the simplified model, there is a strong recommendation that :term:`morphophonemes <morphophoneme>` inicate clearly what phonemes it may correspond on the surface, e.g. use ``{aä}`` if it represents an alternation between ``a`` and ``ä``.  It is recommended to use curly braces to indicate morphophonemes.  The syntax for expressions has been simplified so that these special characters are now free for that purpose.  The morphophonemes must never occur as output symbols, e.g. ``{äa}:{aä}`` is not recommended.

.. index:: deletion

3. :term:`Deletion <deletion>` and :term:`epenthesis` are not treated as :term:`epsilons <epsilon>`.  Instead, a deletion is represented as a concete :term:`zero symbol <zero>`, e.g. ``Ø`` on the surface level.  The corresponding lexical symbol is always a morphophoneme, e.g. ``{pØ}``.  In the lexical representations, epenthesis is also represented as a morphophoneme, e.g. as ``{Øh}`` if, in the surface forms, an ``h`` alternates with nothing according to the context.  In such cases, the surface form of the examples has a zero ``Ø`` in that position.  Different surface allomorphs are made equally long by inserting zeros as needed.

4. The twol.py compiler is incremental as it compiles each rule separately and immediately tests the newly compiled rule against positive and negative examples.  See :doc:`twdiscov`, :doc:`compiletest` and :doc:`twrule` for further information.

.. index:: alphabet

5. *Alphabet* is not declared in the grammar.  The set of lexical and surface symbols and the set of feasible pairs is extracted from the examples.
     
.. index:: sets
     
6. There is no separate way for declaring *sets of symbols*.  They are handled in a concise way by definitions.
     
.. index:: definitons
     
7. Definitions are identified just by an equal sign, (i.e. no heading for definitions), e.g.::

       Glide = {ij}: | j ;

8. The syntax for expressions has been revised so that it reflects a calculus which is closed under its operations, i.e. expressions always denote sets of strings made out of allowed symbol pairs.  See a separate section :doc:`formalism` for the definition of the new syntax.

9. Rules have no *titles*.  The left-hand side serves as the identification, e.g.::
       
       {ij}:j <=> SurfVowel _ SurfVowel ;
       
10. There is usually a separate rule *for each morphophoneme* or sometimes a couple of rules, there are no shorthands for abbreviationg several rules into one (such as the *where* clause).

.. index::
   pair: conflict; detection
   pair: conflict; resolution
	
11. Neither *conflict detection* nor *conflict resolution* exists.  They are not needed because each morphophoneme gets a rule of its own.  There is no point in merging contexts of separate rules.
     
.. index::
   pair: curly; braces
	
12. Rules may have several contexts but contexts are *separated by a comma* instead of a semicolon, e.g.::
       
       {ij}:i => SurfCons _ , _ SurfCons ;
       


