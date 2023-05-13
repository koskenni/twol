.. index:: rule discovery, discovery

.. _discovery:

===============================
Discovering raw two-level rules
===============================

The ``twol-discov`` program reads in a set of two-level examples which consist of space-separated :term:`pair symbols <pair symbol>` (or pairsyms) and the program produces tentative two-level rules for a given :term:`morphophoneme <morphophoneme>`. 

.. index:: positive examples

Positive examples
=================

The method is based on producing positive and negative examples which are specific to one pair symbol.  The *positive examples* consist of all examples which contain that pair symbol, e.g. the following instances of ``{ao}:o``::

  k a l {ao}:o {ij}:i s s {aä}:a
  k a l {ao}:o {ij}:i {Øh}:h {V}:i {nØ}:n
  k a l {ao}:o {ij}:j e {nØ}:n
  k a l {ao}:o {ij}:j {Øt}:Ø {aä}:a

From these full words, the program produces a set of *positive contexts* by separating the left and the right context and removing the symbol pair (e.g. ``{ao}:o``) we are studying::

  {(".#. k a l", "{ij}:i s s {aä}:a .#.") ,
   (".#. k a l", "{ij}:i {Øh}:h {V}:i {nØ}:n .#.") ,
   (".#. k a l", "{ij}:j e {nØ}:n .#.") ,
   (".#. k a l", "{ij}:j {Øt}:Ø {aä}:a .#.")}

Note that an end of string marker has been inserted to the context strings.


.. index:: negative examples

Negative examples
=================

The *negative contexts* are made from positive contexts for related symbol pairs, i.e. all pairs with the same morphophoneme but with a different surface symbol.  The union of such context sets has all negative examples we need, but sometimes, it may also include some correct contexts.  Thus, from this union, the program subtracts possible true positive contexts.  (This happens when the rules are optional.)  The difference yields the desired set of negative contexts for this pair symbol (e.g. ``{ao}:o``)::
  
  {(".#. k a l", ".#."),
   (".#. k a l", "{nØ}:n .#."),
   (".#. k a l", "{ii}:i {nØ}:n .#."),
   (".#. k a l", "{nrs}:n {aä}:a .#."),
   (".#. k a l", "{Øh}:h {V}:a {nØ}:n .#."),
   (".#. k a l", "{Øh}:Ø {V}:a {nØ}:n .#."),
   (".#. k a l", "{Øt}:Ø {aä}:a} .#.")}

These sets of negative contexts for all pairs with the morphophoneme are constructed and saved for further processing of the rules, they will not be reduced during the process.


Initial rules
=============

The script processes rule contexts incrementally.  The initial set of contexts is made directly out of the set of positive contexts for the pair symbol: Each line in the examples that contains the relevant pair symbol forms a rule context so that anything to the left of the pair is the left context and anything to the right is the right context, e.g. the following initial rule::
  
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
2. One can define phonologically motivated sets such as vowels, consonants, or front vowels.  The program will, then, try to replace pair symbols belonging to that set with the name of the set.  The reduction is done only if  all instances can be reduced without compromising the disjointness of positive and negative examples.  Both individual characters and previously produced set names can be reduced.
3. One can replace some pairs (e.g. ``{ao}:a``, ``{aØ}:a`` and ``a``) with a set representing all pairs whose output (i.e. surface) character is the same (i.e. ``:a``).  This replacement is restricted by a set whose pair symbols are considered.  The reduction is done only if it can be applied to all instances of pair symbols in the set without compromising the disjointness.
4. One can replace, similarly, sets of pair symbols (e.g. ``{ij}:i`` and ``{ij}:j``) with the input (i.e. morphophonemic) symbol (i.e. ``{ij}:``).


Recipes
=======

The rule discovery follows so called recipes.  The program is given a list of recipes which will be followed and each recipe will produce a tentative set of rules, a rule for each possible pair with the morphophoneme.  The results of each recipe will be evaluated and the best selection will be printed out.

A recipe is a sequence of steps or tasks selected from the selection of generalisations or reductions presente in the previous section.  The reductions are applied tentatively to the current positive set of contexts of a pair symbol.  If the result is still disjoint from the negative context set of the pair symbol, then the process continues with the newly reduced positive context set.  Otherwise the tentative reduction is discarded and the next step of the recipe is tried.


Rules as sets of context
========================

The set of positive contexts for a pair symbol represents the evolving rule.  The set of contexts is then changed with the operations listed in the above section `Generalisations`_.  The newly reduced positive tentative context set is then compared with the constant set of negative contexts.  As the positive contexts may contain names of pair symbol sets instead of concrete symbols, the disjointness is tested with an appropriate function.  Matching is done context by context.  The left and right context are strings which are converted to lists of symbols.  A pair symbol in the positive context matches only the same pair symbol in the negative context.  A set symbol matches any pair symbol belongint to that set.

Each reduction is done first tentatively.  If the sets remain disjoint, then the program may accomplishes the reduction and continues by testing whether further reductions would be possible.  If the reduction fails by making the sets overlapping, then the reduction is ignored, and possible other reductions are tested against the situation before the failed reduction.

Mathematically, one can interpret the reductions to multiply the sets of context (i.e. string pairs) to list lots of strings, separate ones for each possible expansion (a single symbol pair to the set of all possibilites in the reduction).  Reducing a set correspond to introducing distinct strings for each member of the set.  Similarly, truncation would be interpreted as a replacement where the truncated pair symbols are substituted, in turn, with all possible pair symbols (mathematically, but not in practice).

Reductions may, in general, cause disjoint positive/negative context sets become ovelapping, but never the opposite.  A reduction must not be able to convert an overlapping context sets become disjoint.  The reductions presented earlier, are safe in this respect.


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

See the :ref:`formalism` for details of the rule formalism, especially for the ``.m`` operator.  The program uses a subset (``discovdef.ebnf``) of the rule formalism, but builds Python sets instead of finite-state transducers.


Recipes to control the order of reductions
==========================================

The user defines a set of recipes i.e. lists of tentative reductions.  Each list produces a rule or a pair of rules for each of the pairs containing the given morphophoneme.  Each list of reductions is executed separately and thus usually produce different raw rules.  Lists of recipes are given as JSON files.  A simple list of two recipes could be::

  [
    [
	{"op": "truncate", "side": "left"},
	{"op": "truncate", "side": "right"}
    ],
    [
	{"op": "truncate", "side": "left"},
	"ConM",
	"VowS",
	"VowØ",
	{"op": "truncate", "side": "right"}
    ]
  ]


Evaluating the rules discovered
===============================

The program applies each recipe separately and stores the rules that are produced.  In addition, the goodness of each result is evaluated.  The raw rules are evaluated with a simple criterion which is the product of three components: (1) the number of contexts in the rule, (2) the sum of the left and the right context maximum lengths, and (3) the number of different pair symbols or set symbol names in the rule.


The program suggests reasonable raw rules for phenomena where the condition is strictly local, e.g. stem-final vowel alternations and also for consonant gradation in Finnish.  On the other hand, long distance phenomena e.g. vowel harmony cannot be summarized properly by this method as is shown below.

.. index:: =>, right-arrow rule, context-requirement rule, /<=, exclusion rule

The program only produces ``<=>`` and ``=>`` types of rules.  This is not a limitation which would restrict the phenomena which can be expressed.  The double arrow rule is proposed when the phenomenon is deterministic, i.e. there are no contexts where the morphophoneme could correspond to more than one surface symbol.  If more than one surface symbol may correspond, then only rigt arrow rules are proposed.  The  last double arrow rule for a morphophoneme can be discarded if all alternatives would receive a double arrow rule.

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

  ! recipe:
  !               {'op': 'truncate', 'side': 'left'}
  !               {'op': 'truncate', 'side': 'right'}
  {ieeeØ}:Ø <=>           ! 1
       _ {ij}:i ;
  {ieeeØ}:i <=>           ! 4
       _ .#. ,
       _ {CL}:Ø ;
  !                         tupp<i>
  !                         velØ<i>
  !                         laht<i>
  !                          kiv<i>Økin
  !                         laht<e>Øen
  !                         aarn<e>ØØsi
  !                         tupp<e>na
  !                         tupp<e>in
  !                         lahd<e>n
  !                         velj<e>lle
  !                         tupØ<e>n
  !                         tupp<e>Øa
  !                         tupp<e>hen
  !                         laht<e>in
  !                         laht<e>na
  !                         tupp<e>Øen
  !                         laht<e>Øa
  !                         laht<e>hen
  !                         tupp<Ø>iØa
  !                         laht<Ø>ien
  !                         laht<Ø>ihin
  !                         tupp<Ø>iØin
  !                         lahd<Ø>issa
  !                         laht<Ø>iØa
  !                         tupØ<Ø>issa
  !                         tupp<Ø>ien
  !                         laht<Ø>iØin
  !                         tupp<Ø>ihin
  !                         velj<Ø>ille


In the output that is produced for all morphophonemes, one can see that the rules for ``{aä}``, i.e. vowel harmony, are fairly useless, even if they are correct for the example data.  On the other hand, the rules for stem final vowel aternations for ``{ieeØ}`` and ``{iiie}`` are correct and general.  So are the rules for consonant gradation ``{kØ}`` and the slightly more complicated ``{tds}`` alternation.


