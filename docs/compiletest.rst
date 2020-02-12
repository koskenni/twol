.. _compiling:

===============================
Compiling and testing the rules
===============================

Required files and packages
===========================

Before you can start using the ``twol-comp`` compiler, you have to see that all necessary parts are available, usually by installing the ``twol`` package from PyPI, see for more instructions at `wiki <https://github.com/koskenni/twol/wiki>`__.  


File containing examples
========================

Before one writes even the first rule, one has to prepare a file of examples which ought to be carefully selected so that they demonstrate the kinds of alternations that the rules are expected to describe.  One possibility of creating a file of examples is described in the section :doc:`morphophon`.  That method starts from a table of inflected word forms and it produces a set of two-level examples out of the given word forms.  The individual examples consist of strings of blank separated pair symbols which are exactly in the form that is needed for compiling and testing.

Alternatively, one may prepeare a file of examples manually with a program editor (such as Gedit or Emacs).  One must use some linguistic competence when finding the morphophonemic representations for the example words.

Whatever method you are using when you build your set of examples, you end up with a file ``ksk-renamed.pstr`` containing lines like::

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


Rules, compiling and testing
============================

The characteristic feature of the simplified two-level model is that the linguist is *encouraged to write the rules one by one and let the compiler test them immediately against the examples*.  Rules are entirely independent of each other and the linguist can start from any rule and procede as one wishes.  The demanding task of writing a morphophonological grammar is divided into many small and straight-forward tasks of writing a single rule.

Let us try with the morphophoneme ``{ieØeØ}`` and compute the raw rules for it::

  $ twol-discov ksk-renamed.pstr -v 0 -s '{ieØeØ}'
  {ieØeØ}:i =>
       _ .#. ;
  {ieØeØ}:e /<=
       _ t,
       _ .#.,
       _ {Øt}:t,
       _ {ij}:i ;
  {ieØeØ}:Ø =>
       _ t,
       _ {Øt}:t,
       _ {ij}:i ;

Our linguistically oriented eyes see that ``{ieØeØ}:i`` occurs if and only if it is at the end of a word.  Thus we get our first rule::

  {ieØeØ}:i <=> _ .#. ;

This rule says that the pair ``{ieØeØ}:i`` can only occur at the end of a word and also that at the end of a word, other possible realizations (``{ieØeØ}:e`` and ``{ieØeØ}:Ø``) are there forbidden.  Let us write that sinle rule and save it as a file ``rules.twol``.  We can compile and test it against our examples by::

  $ twol-comp.py --thorough 2 examples.pstr rules.twol 
  {ieØeØ}:i <=> _ .#. ;
  All positive examples accepted
  All negative examples rejected

So, the rule accepted all given (positive) examples.  In addition, the ``=>`` part of the rule was tested against negative examples which were produced by setting the output symbol of ``{ieØeØ}`` in the other examples (where ``{ieØeØ}:Ø`` or ``{ieØeØ}:e`` occurred) to ``i`` and checking that the ``=>`` rule rejects them all.  Furthermore, the output symbol of the example where ``{ieØeØ}:Ø`` occurred was changed into ``Ø`` and ``e`` and this was checked against the ``<=`` part of the rule in order to see that the rule allows only ``Ø`` as the output symbol in the context given by the rule.  Therefore, the rule appears to do exactly what we wanted (as far as out set of examples covers the relevant combinations).

Now we can proceed to the second rule for ``{ieØeØ}``.  The third rule proposed by the discovery program needs a bit cleaning.  Let us add to the grammar another rule which says that the morphophoneme may correspond to zero if followed by a ``t`` or an ``i`` on the surface::

  {ieØeØ}:Ø <=> _ :t ,
                _ :i ;

Runing the above compilation again shows that now both rules passed both tests.  Now we are done with the morphophoneme ``{ieØeØ}`` and may proceed to other morphophonemes.

One may adjust the amount of testing the compiler will perform.  The parameter ``--thorough`` (or ``-t``) can be given three different values: **0** for omitting both tests, **1** for testing that the rules accept all examples, and **2** for testing both the positive and negative examples of each rule.

Positive tests should always pass, if the rule is correct.  Negative examples should usually be all rejected, but not in all cases.  Sometimes there are two rules where one depends on the effect of the other, some negative tests fail.  The wrong ones accepted by the first rule would, indeed, be rejected by the second rule, but the other rule is not available yet.

There is another type of negative tests which is done after all rules have been seen and compiled.  Then, a total set of negative examples is created and this is tested against the combination of all rules.  Then, no negative examples should remain.  This test is not reasonable before all morphophonemes have rules.  These collective tests for all rules can be chosen by givin additional parameters on the command line:

  ``--lost`` filename, ``-l`` filename
    If a value is given to this parameter, a FST file is written containing all positive examples which were rejected by at least one rule.  Here we do not know which rule caused this.

  ``--wrong`` filename, ``-w`` filename
    If a value is given to this parameter, a FST file is written containing all negative examples which were accepted by all rules.  Again, we do not know which rule ought to have rejected them.

The results are FSTs, so we cannot look at them directly.  We can use the ``hfst-fst2strings`` tool for looking at their contents, e.g.::

  $ hfst-fst2strings -i wrong.fst | less

