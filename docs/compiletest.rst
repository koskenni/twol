.. _compiling:

===============================
Compiling and testing the rules
===============================

Required files and packages
===========================

Before you can start using the ``twol-comp`` compiler, you have to see that all necessary parts are available.  In order to run properly, the compiler needs:

1. modules *twexamp.py*, *cfg.py*, *fs.py*, *twbt.py*, *twparser.py*, *twrule.py* and *twolcsyntax.ebnf* which come along when you perform ``git clone`` or ``git pull`` commands

2. the ``hfst`` Python interface which you install (if you do not have it already) by::

     python3 -m pip install hfst

3. a parser generator package called ``tatsu`` which you can install (if you do not have it yet) by::

     python3 -m pip install tatsu


File containing examples
========================

Before one writes even the first rule, one has to prepare a file of examples which ought to be carefully selected so that they demonstrate the kinds of alternations that the rules are expected to describe.  One possibility of creating a file of examples is described in the section :doc:`morphophon`.  That method starts from a table of inflected word forms and it produces a set of two-level examples out of the given word forms.  The individual examples consist of strings of blank separated pair symbols which are exactly in the form that is needed for compiling and testing.

Alternatively, one may prepeare a file of examples manually with a program editor (such as Gedit or Emacs).  One must use some linguistic competence when finding the morphophonemic representations for the example words.

Whatever method you are using when you build your set of examples, you end up with a file ``examples.pstr`` containing lines like::

  t u o h {ieØeØ}:i
  t u o h {ieØeØ}:e n
  t u o h {ieØeØ}:Ø {Øt}:t {aä}:a
  t u o h {ieØeØ}:e {nrs}:n {aä}:a
  t u o h {ieØeØ}:e {Øh}:Ø {V}:e n
  t u o h {ieØeØ}:e {Øh}:h {V}:e n
  t u o h {ieØeØ}:Ø {ij}:i s s {aä}:a
  t u o h {ieØeØ}:Ø {ij}:i e n
  t u o h {ieØeØ}:Ø t e n
  t u o h {ieØeØ}:Ø {ij}:i {Øt}:Ø {aä}:a
  t u o h {ieØeØ}:Ø {ij}:i {Øh}:Ø {V}:i n
  t u o h {ieØeØ}:Ø {ij}:i {Øh}:h {V}:i n

One can use this file directly with the ``twol.py`` compiler or convert the file into a FST to be more efficient for the compiler to load in by executing the following command::

  python3 twexamp.pl examples.pstr examples.fst


Rules, compiling and testing
============================

The small set of examples given above has quite a lot of information about a morphophoneme ``{ieØeØ}`` so that one could write the very first rule and save it as a file ``rules.twol``::

  {ieØeØ}:i <=> _ .#. ;

This rule says that the pair ``{ieØeØ}:i`` can only occur at the end of a word and also that at the end of a word, other possible realizations (``{ieØeØ}:e`` and ``{ieØeØ}:Ø``) are there forbidden.

The simple grammar can now be tested against the examples by::

  $ twol-comp.py --thorough 2 examples.pstr rules.twol 
  
  
  
  {ieØeØ}:i <=> _ .#. ;
  All positive examples accepted
  All negative examples rejected

So, the rule not only accepted all examples but it also rejected the negative examples which were produced by setting the output symbol of ``{ieØeØ}`` in the other examples to ``i`` and the output symbol of the first example word into ``Ø`` and ``e``.  Let us add to the grammar another rule which says that the morphophoneme may correspond to zero if followed by a ``t`` or an ``i`` on the surface::

  {ieØeØ}:Ø <=> _ :t , _ :i ;

The result will tell that now both rules passed both tests.  It is recommended to write one rule at a time and test it immediately.

One may adjust the amount of testing the compiler will perform.  The parameter ``--thorough`` (or ``-t``) can be given three different values: **0** for omitting both tests, **1** for testing that the rules accept all examples, and **2** for testing both the positive and negative examples of each rule.

Positive tests should always pass, if the rule is correct.  Negative examples are usually also all rejected, but not in all cases.  If there are two rules where one depends on the effect of the other, the negative tests fail.  The wrong ones accepted by the first rule would, indeed, be rejected by the second rule, but the other rule is not available yet.  There is another type of negative tests which is done after all rules have been seen and compiled.  Then, a total set of negative examples is created and this is tested against the combination of all rules.  Then, no negative examples should remain.  This test is not reasonable before all morphophonemes have rules.  These collective tests for all rules can be chosen by givin additional parameters on the command line.

  ``--lost`` filename, ``-l`` filename
    If a value is given to this parameter, a FST file is written containing all positive examples which were rejected by at least one rule.  Here we do not know which rule caused this.

  ``--wrong`` filename, ``-w`` filename
    If a value is given to this parameter, a FST file is written containing all negative examples which were accepted by all rules.  Again, we do not know which rule ought to have rejected them.

The results are FSTs, so we cannot look at then directly.  We can use the ``hfst-fst2strings`` tool for looking at their contents, e.g.::

  $ hfst-fst2strings -i wrong.fst | less

