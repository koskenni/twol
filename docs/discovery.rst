.. index:: rule discovery, discovery

.. _discovery:

===============================
Discovering raw two-level rules
===============================

The ``twol-discov`` program reads in a set of two-level examples which consist of space-separated :term:`pair symbols <pair symbol>` and the program produces tentative two-level rules for a given :term:`morphophoneme <morphophoneme>`.  The program can be used with the final set of examples or some intermediate stage of the example set where only a part of the morphophonemes are in their final form, if one can search for contexts which refer only to the surface characters (such as ``:a`` or surface consonant).

.. index:: positive examples

Positive examples
=================

The method is based on producing positive and negative examples which are specific to one morphophoneme.  The *positive examples* consist of all examples which contain that morphophoneme, e.g. the following instances of ``{ao}``::

  k a l {ao}:a
  k a l {ao}:a {nØ}:n
  k a l {ao}:a {ii}:i {nØ}:n
  k a l {ao}:a {nrs}:n {aä}:a
  k a l {ao}:a {Øh}:h {V}:a {nØ}:n
  k a l {ao}:a {Øh}:Ø {V}:a {nØ}:n
  k a l {ao}:a {Øt}:Ø {aä}:a
  k a l {ao}:o {ij}:i s s {aä}:a
  k a l {ao}:o {ij}:i {Øh}:h {V}:i {nØ}:n
  k a l {ao}:o {ij}:j e {nØ}:n
  k a l {ao}:o {ij}:j {Øt}:Ø {aä}:a


.. index:: negative examples

Negative examples
=================

The *negative examples* are made from the positive ones by distorting the occurrences of the morphophoneme.  Each occurrence is replaced by all correct and incorrect pairs of that morphophoneme.  This results in all negative examples we need, but it also produces some correct examples.  Thus, from this preliminary set, the program subtracts all positive examples which yields the desired set of negative examples for this morphophoneme, e.g.::
  
  k a l {ao}:o
  k a l {ao}:o {nØ}:n
  k a l {ao}:o {ii}:i {nØ}:n
  k a l {ao}:o {nrs}:n {aä}:a
  k a l {ao}:o {Øh}:h {V}:a {nØ}:n
  k a l {ao}:o {Øh}:Ø {V}:a {nØ}:n
  k a l {ao}:o {Øt}:Ø {aä}:a
  k a l {ao}:a {ij}:i s s {aä}:a
  k a l {ao}:a {ij}:i {Øh}:h {V}:i {nØ}:n
  k a l {ao}:a {ij}:j e {nØ}:n
  k a l {ao}:a {ij}:j {Øt}:Ø {aä}:a


Initial rules
=============

The script processes rule contexts incrementally.  The initial set of contexts is made out of the positive examples as such: Each line in the examples that contains the relevant pair symbol forms a rule context so that anything to the left of the pair is the left context and anything to the right is the right context, e.g. the following two initial rules::
  
  {ao}:a =>
    .#. k a l _ .#. ,
    .#. k a l _ {nØ}:n .#. ,
    .#. k a l _ {ii}:i {nØ}:n .#. ,
    .#. k a l _ {nrs}:n {aä}:a .#. ,
    .#. k a l _ {Øh}:h {V}:a {nØ}:n .#. ,
    .#. k a l _ {Øh}:Ø {V}:a {nØ}:n .#. ,
    .#. k a l _ {Øt}:Ø {aä}:a .#. ;

  {ao}:o =>
    .#. k a l _ {ij}:i s s {aä}:a .#. ,
    .#. k a l _ {ij}:i {Øh}:h {V}:i {nØ}:n .#. ,
    .#. k a l _ {ij}:j e {nØ}:n .#. ,
    .#. k a l _ {ij}:j {Øt}:Ø {aä}:a .#. ;

There will initially be as many contexts parts in the rule as there are occurrences of the pair symbol.  Such a rule trivially accepts all positive examples and rejects all negative examples (but reject many good occurrences beyond the set of given examples).  The idea of the algorithm is to generalise the contexts in steps.  E.g. shorter contexts still accept the positive examples but they do not necessarily reject all negative ones.  Thus, after each step, the program has to check that the rules still rejects the set of all examples.  As long as they do reject, the process can go on.


Generalisations
===============

There are several types of generalisations are available:

1. One can truncate the left or the right context to a given maximum length.  If the truncation fails, then the program tries to truncate one pair symbol less until the truncation succeeds or nothing was truncated.
2. One can replace some pairs (e.g. ``{ao}:a``, ``{aØ}:a`` and ``a``) with a set representing all pairs whose surface character is the same (i.e. ``:a``).  The program has two options: either it will try to reduce all pair symbols in one step, or it will try each surface symbol separately.
3. One can define phonologically motivated sets such as vowels, consonants, or front vowels.  The program will, then, try to replace pair symbols belonging to that set with the name of the set.


Rules as sets of pairs of strings
=================================

One could perform the testing by building actual two-level rules and compile them before testing them against the positive and the negative sets.  The program takes, however, a short cut by representing the rules by context pair sets, i.e. for ``{ao}:o =>`` rule the set of positive context pairs would be::

  {(".#. k a l", "{ij}:i s s {aä}:a .#.") ,
   (".#. k a l", "{ij}:i {Øh}:h {V}:i {nØ}:n .#.") ,
   (".#. k a l", "{ij}:j e {nØ}:n .#.") ,
   (".#. k a l", "{ij}:j {Øt}:Ø {aä}:a .#.")}

The set of negative contexts for ``{ao}:o =>`` would be::

  {(".#. k a l", ".#.") ,
   (".#. k a l", "{nØ}:n .#.") ,
   (".#. k a l", "{ii}:i {nØ}:n .#.") ,
   (".#. k a l", "{nrs}:n {aä}:a .#.") ,
   (".#. k a l", "{Øh}:h {V}:a {nØ}:n .#.") ,
   (".#. k a l", "{Øh}:Ø {V}:a {nØ}:n .#.") ,
   (".#. k a l", "{Øt}:Ø {aä}:a .#.") ;

Note that the elements of these sets are pairs or tuples of Python strings.  The positive and the negative set would overlap only if there is an identical tuple in both.  Using this representation one can test tentative rules by using native Python operations without compiling the two-level rules into finite-state transducers.

When we use this representation for the rules, all reductions must be applied both to the positive and the negative set of contexts, and the application must be consistent in both sets.  Each reduction is done first tentatively.  If the sets remain disjoint, then the program may accomplishes the reduction and continues by testing whether further reductions would be possible.  If the reduction fails by making the sets overlapping, then the reduction is ignored, and possible other reductions are tested against the situation before the failed reduction.

Mathematically, one can interpret the reductions to multiply the sets of context (i.e. string pairs) to list lots of strings, separate ones for each possible expansion (a single symbol pair to the set of all possibilites in the reduction).  Reducing a set correspond to introducing distinct strings for each member of the set.  Similarly, truncation would be interpreted as a replacement where the truncated pair symbols are substituted, in turn, with all possible pair symbols (mathematically, not in practice).

Reductions may, in general, cause disjoint positive/negative context become ovelapping, but never the opposite.  A reduction must not be able to convert an overlapping context sets become disjoint.


Defining sets of pair symbols
=============================

The ``twol-discover`` program defines the sets of pair symbols using the same formalism as the ``twol-comp`` with the restriction that one can only define sets that are one character wide and no rules.  Thus, a typical definition could be::

  $ cat setdefs.twol
  VoSF = :ä | :ö | :y ;       ! front vowels
  VoSB = :a | :o | :u ;       ! back vowels
  VoSN = :e | :i ;            ! neutral vowels
  VoS = VoSF | VoSB | VoSN ;  ! surface vowels
  VoM = VoS.m ;               ! morphophonemic vowels
  VoØ = VoM - VoS ;           ! deleted vowels
  CoS = :b | :d | :h | :k |   ! surface consonanta
        :l | :m | :n | :p |
	:r | :s | :t | :v | j ;
  CoM = CoS.m ;               ! morphophonemic consonants
  CoØ = CoM - CoS ;           ! deleted consonants

See the :ref:`formalism` for details of the rule formalism, especially for the ``.m`` operator.  The program uses a subset (``discovdef.ebnf``)of the rule formalism, but builds Python sets instead of finite-state transducers.


Recipes to control the order of reductions
==========================================

The user defines a set of recipes i.e. lists of tentative reductions.  Each list produces a rule or a pair of rules for each of the pairs containing the given morphophoneme.  Each list of reductions is executed separately and thus usually produce different raw rules.  Lists of recipes are given as JSON files.  A simple list of two recipes could be::

  [
    [
      ["surface-all"],
      ["truncate-left", 0],
      ["truncate-right", 0]
    ],
    [
      ["truncate-left", 0],
      ["VoS"],
      ["VoØ"],
      ["CoM"],
      ["truncate-right", 0]
    ]
  ]

The program applies each recipe separately and stores the rules that are produced.  In addition, the goodness of each result is evaluated.  The raw rules are evaluated with a simple criterion which is the product of three components: (1) the number of contexts in the rule, (2) the sum of the left and the right context maximum lengths, and (3) the number of different pair symbols or set symbol names in the rule.


The program suggests reasonable raw rules for phenomena where the condition is strictly local, e.g. stem-final vowel alternations and also for consonant gradation in Finnish.  On the other hand, long distance phenomena e.g. vowel harmony cannot be summarized properly by this method as is shown below.

.. index:: =>, right-arrow rule, context-requirement rule, /<=, exclusion rule

The program only produces ``=>`` and ``/<=`` types of rules.  This is not a limitation which would restrict the phenomena which can be expressed.  Indeed, when some phenomena are optional, using just these two types of rules makes it easy to allow for free variation.

Even in the best case, the rules can only be as good as the set of examples are. If the examples are chosen in a disciplined and balanced manner, the program is expected to be useful and practical.  If alternations are only partly present in the set of examples, the proposed raw rules will be poor and may even be misleading.

For more information on the program itself, see the documentation of the program code ``discover`` in the :doc:`modules` and directly in :doc:`twol.discover`.

.. index:: twol-discov

Using ``twol-discov``
=====================

The input for this script must be in the same format as the examples given to the ``twol-comp`` rule compiler and tester, e.g.::

  m ä {kØ}:k {ieeØ}:i
  m ä {kØ}:Ø {ieeØ}:e n
  m ä {kØ}:Ø {ieeØ}:e s s {aä}:ä
  m ä {kØ}:k {ieeØ}:e n {aä}:ä
  m ä {kØ}:Ø {ieeØ}:Ø i s s {aä}:ä
  k ä {tds}:s {ieeØ}:i
  k ä {tds}:d {ieeØ}:e n
  k ä {tds}:d {ieeØ}:e s s {aä}:ä
  k ä {tds}:t {ieeØ}:e n {aä}:ä
  k ä {tds}:s {ieeØ}:Ø i s s {aä}:ä
  l a s {iiie}:i
  l a s {iiie}:i n
  l a s {iiie}:i s s {aä}:a
  l a s {iiie}:i n {aä}:a
  l a s {iiie}:e i s s {aä}:a
  l a {kØ}:k {iiie}:i
  l a {kØ}:Ø {iiie}:i n
  l a {kØ}:Ø {iiie}:i s s {aä}:a
  l a {kØ}:k {iiie}:i n {aä}:a
  l a {kØ}:Ø {iiie}:e i s s {aä}:a

The program collects the input and the output alphabets and the allowed symbol pairs from the examples, thus no other definitions are needed.  The program produces output such as::

   $ twol-discov demo-raw.pstr
   {aä}:a =>
       {kØ}:Ø {iiie}:i s s _  ;
       s {iiie}:i s s _  ;
       a {kØ}:k {iiie}:i n _  ;
       {iiie}:e i s s _  ;
       a s {iiie}:i n _  ;
   {aä}:ä =>
       {ieeØ}:Ø i s s _  ;
       {tds}:d {ieeØ}:e s s _  ;
       {kØ}:Ø {ieeØ}:e s s _  ;
       ä {tds}:t {ieeØ}:e n _  ;
       ä {kØ}:k {ieeØ}:e n _  ;
   {ieeØ}:e =>
	_ n ;
	_ s ;
   {ieeØ}:i =>
	_ .#. ;
   {ieeØ}:Ø =>
	_ i ;
   {iiie}:e =>
	_ i ;
   {iiie}:i /<=
	_ i ;
   {kØ}:k =>
	_ {ieeØ}:i .#. ;
	_ {iiie}:i .#. ;
	_ {iiie}:i n {aä}:a ;
	_ {ieeØ}:e n {aä}:ä ;
   {kØ}:Ø /<=
	_ {ieeØ}:i .#. ;
	_ {iiie}:i .#. ;
	_ {iiie}:i n {aä}:a ;
	_ {ieeØ}:e n {aä}:ä ;
   {tds}:d =>
	_ {ieeØ}:e s s ;
	_ {ieeØ}:e n .#. ;
   {tds}:s /<=
	_ {ieeØ}:e ;
   {tds}:t =>
	_ {ieeØ}:e n {aä}:ä ;

In the output, you can see that the rules for ``{aä}``, i.e. vowel harmony, are fairly useless, even if they are correct for the input data.  On the other hand, the rules for stem final vowel aternations for ``{ieeØ}`` and ``{iiie}`` are almost correct and general.  So are the rules for consonant gradation ``{kØ}`` and the slightly more complicated ``{tds}`` alternation.


