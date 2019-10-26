.. _formalism:

==============
Rule formalism
==============

In the simplified two-level model, much information is extracted out of the examples.  No rules may be compiled without a set of two-level examples in the so called :term:`symbol pair` string representation.  The examples are in a file consisting of lines like::

  m ä {kØ}:Ø {ieeØ}:e s s {aä}:ä


A two-level grammar consists of:

(a) Definitions which give names for expressions so that these names can be used in subsequent rules and definitions.  A definition consists a name, an equal sign and an expression and it is terminated in a semicolon.

(b) Rules which constrain the occurrences of a or some symbol pairs in the examples.  Rules contain a center or X part whose occurrences the rule constrain, an operator, and one or more contexts separated by a comma.

(c) Comments which are useful for understanding what the definitions and the rules are supposed to do.  An *exclamation mark* (!) marks a comment: anything that follows on that line is just a comment and is not processed by the compiler.

The following is a simple example of a complete two-level rule grammar::

  ! demo-rules.twol
  VowS = [:a|:e|:i|:ä] ;         ! surface vowels
  VowM = VowS.m ;                ! morphophonemic vowels
  ConL = :k|:l|:m|:n|:s ;        ! surface consonants
  ConM = ConL.m ;                ! morphophonemic consonants

  {iiie}:e <=> _ i ;
      ! las<e>issa la<e>issa
  {ieeØ}:i <=> _ :Ø* .#. ;
      ! mäk<i> käsi<i>
  {ieeØ}:Ø <=> _ i ;
      ! mä<>issä käs<>issä
  {kØ}:Ø <=> _ VowM (i) ConM :Ø* .#. ,
	     _ VowM (i) ConM ConM ;
      ! mä<k>i mä<>essä mä<>issä la<k>i la<>issa la<>eissa 
  {tds}:s <=> _ :Ø* :i ;
      ! kä<s>i
  {tds}:d => _ VowM ConM :Ø* .#. ,
	     _ VowM ConM ConM ;
      ! kä<d>essä
  {tds}:t => _ VowS :Ø* .#. ,
	     _ VowS (ConM) VowS ;
      ! kä<t>enä
  {aä}:a <=> :a :* _ ;
      ! kädess<ä> käsiss<ä> lasiss<a> 

A definition has an *equal sign* (=).  The name before the equal sign is the *name* (e.g. ``VowS``) defined for the *expression* (``[:a|:e|:i|:ä]``) that follows the equal sign (up to the semicolon (;) which terminates the definition).  A definition may extend over several lines if necessary.

Rules have a *rule operator* ``=>``, ``/<=``, or ``<=>`` or ``<=``.  To the left of the operator, there is an expression which is called the *center* of of the rule (e.g. ``{ieeØ}:Ø``), and to the right there must be one or more *context* (e.g. ``_ i``) for the rule.  If there are more than one context, the contexts are separated by a comma from each other.  The rule is terminated by a semicolon.  Each context consists of a *left context* (which may be empty) and a *right context* (e.g. ``i``) which are separated from each other by an underscore (``_``).

-----------
Expressions
-----------

Let us call the set of all :term:`symbol pairs <symbol pair>` that occur in the examples *Pairs*. *Two-level expressions* (TLEs) denote sets of strings made out of such pairs.  TLEs use :term:`pair symbols <pair symbol>` with a colon (such as ``a`` and ``{aä}:a``) to denote pairs (e.g. ``('a', 'a')`` and ``('{aä}', 'a')``).  Pair symbols with identical components (e.g. ``a:a``) are usually abbreviated as a single symbol (e.g. ``a``).

TLEs denote sets of pair symbol strings.  In order to define some operations within TLEs we need to talk about *input (or upper) projections, (X.u),* and *output (or lower) projections, (X.l),* of such strings.  The input projection of a pair-symbol string is a string of the left parts of the symbol pairs, and the output projection of the right parts of the symbol pairs.  For sets the projection is made to each member in the set.  These projections represents sets of strings which are not TLEs but are used as concepts to define some operations within TLEs.

TLEs may consist of:

*x:y* (a pair symbol)
    A pair-symbol which occurs in the examples, e.g. ``{aä}:a``, ``{uØ}:Ø``, ``a``, is a valid TLE denoting a string consisting of that pair-symbol.  Note that the simplified two-level model does not use pairs like ``a:ä`` where two distinct surface symbols would be a pair.  Note that a morphophoneme without the colon, e.g. ``{aä}`` as well as a plain zero ``Ø`` is usually an error.

*x:Ø* (:term:`deletion`, :term:`zero`)
    Deletion, e.g. ``{kØ}:Ø``, is represented by an arbitrary symbol such as ``Ø`` which is not otherwise used in the language to be described.  The zero is treated as a normal symbol within the rules and examples (thus, not as an epsilon or null string).  Compilation and testing is done with ``Ø`` as a character.  That character is deleted when building a recognizer for analyzing actual word forms in texts.  Note that ``Ø`` is not a valid pair symbol and that morphophonemic representations never contain ``Ø`` as a symbol.  All deletions and ephentheses are treated by using morphophonemes which contain zero as one of its possibilities, e.g. ``{ieØ}``

*:z* (morphophonemic side open)
    Denotes the set of those pair symbols *x:y* in *Pairs* where *y* = *z*.  E.g. ``:a`` might denote the set of strings ``a``, ``{aä}:a`` and ``{aØ}:a``.

*z:* (surface side open)
    Denotes the set of those pair symbols *x:y* in *Pairs* where *x* = *z*.  E.g. ``{ij}:`` might denote the set of ``{ij}:i`` and ``{ij}:j``

*:* (both sides open)
   Denotes the *Pairs* set, i.e. one symbol pair out of the whole inventory of symbol pairs in the examples.

*X Y* (concatenation)
   Denotes the set of strings *x y* where *x* is in *X* and *y* is in *Y*, e.g.  if ``:a`` contains ``a`` and ``{aä}:a`` and ``:i`` contains ``i`` and ``{ij}:i`` then ``:a :i`` contains ``a i``, ``a {ij}:i``, ``{aä}:a i`` and ``{aä}:a {ij}:i``.
 
*X|Y* (disjunction, union, or)
    Denotes the union of the sets represented by *X* and *Y*.  E.g. if ``:m`` contains ``m`` and ``{mn}:m`` and ``:n`` contains ``n`` and ``{mn}:n`` then ``:m|:n`` contains ``m``, ``{mn}:m``,  ``n`` and ``{mn}:n``.

*X** (Kleene star)
    Denotes zero, one or more concatenations of *X*,  E.g ``:Ø*`` would contain the null string, ``:Ø``, ``:Ø :Ø``, etc..

*X+* (Kleene plus)
    Denotes one or more concatenations of *X*,  E.g ``:Ø*`` would contain ``:Ø``, ``:Ø :Ø``, etc..

*X.m* (morphophonemic projection, surface completion)
    Morphophonemic projection does the same kind of expansion for general TLEs as dropping the right component of a pair does for a pair, e.g. when ``{aä}:a`` is replaced by ``{aä}:`` .  Consider first the input (or upper side) projection *X.u* of *X*.  *X.u* consists of all morphophonemic versions of the strings in *X* (consisting of the left components of the pair-symbols).  Then, *X.m* is the set of pair-symbol strings in *Pairs** whose input projection is *X.u*.  E.g. if ``:e`` contains ``e`` and ``{ieØ}:e`` then ``:e.u`` would consist of ``e`` and ``{ieØ}``.  Then, ``:e.m`` could consist of ``e``, ``{ieØ}:e`` and ``{ieØ}:Ø``.

*X.s* (surface projection, morphophonemic completion)
    Surface projection does the same kind of expansion for general TLEs as dropping the left component of a pair does for a pair, e.g. when ``{aä}:a`` is replaced by ``:a`` .  Consider first the output (or lower side) projection *X.l* of *X*.  *X.l* consists of all surface sides of the strings in *X* (consisting of the right components of the pair-symbols).  Then, *X.l* is the set of pair-symbol strings in *Pairs** whose output projection is *X.l*.  E.g. if ``{ao}:`` contains ``{ao}:a`` and ``{ao}:o`` then ``{ao}:.l`` would consist of ``a`` and ``o``.  Then, ``{ao}:.s`` could consist e.g. of ``a``, ``o``, ``{ao}:a``,  ``{ao}:o``,  ``{aä}:a``, and ``{oö}:o``.

*X&Y* (conjunction, intersection, and)
    The conjunction of two TLEs *X* and *Y* denotes the intersection of the string sets of the component expressions, e.g. ``Vo & :Ø`` could represent all vowels which are deleted on the surface.

*X-Y* (relative difference, minus)
    The difference of two TLEs *X* and *Y* denoes the set of strings *z* which are in *X* but not in *Y*.

*[X]* (brackets, grouping)
    A TLE in square brackets denotes itself but the brackets affect the order of evaluation, e.g. ``:e :i | :a :u`` consists of strings of length two whereas ``:e [:i | :a] :u`` would consist of strings of lenght three.

*(X)* (optional)
    An optional TLE *X* denotes the union of *X* and a set consisting of the zero-length string (epsilon).

*.#.* (left or right end of the string)
    When occurring in a left (resp.  right) context part, *.#.* denotes the left (resp.  right) end of the symbol pair string.  It does not correspond to any concrete symbol in a compiled rule, it just quarantees that there is nothing before (resp.  after) that point.

Note that composition ``.o.``, cross product ``.x.``, input (or upper) project ``.u``, output (or lower) project ``.l``, and inverse ``.i`` are not well-defined within the strings constructed out of symbols in *Pairs*.  These operations would easily produce strings which are not in *Pairs**.  Furthermore, one may express set differences in TLEs but there is no unary minus.  


---------------
Two-level rules
---------------

There are four types of two-level rules:

**=>**
    A **context requirement rule** (or a right arrow rule) says that the expressions matching the center or X part of the rule may only occur if surrounded by one of the contexts given in the rule.

**<=**
    An **output coercion rule** (or a surface coercion rule or a left arrow rule) says that the input side of *X* must correspond to one of the possibilities given in *X* in the contexts given by the rule.  In other words, *X.m - X* may not occur in any of the contexts given by the rule.  Thus *X <= LC _ RC* is equivalent to *X.m - X /<= LC _ RC*

``<--``
    An **input coercion rule** says that the output side of *X* must correspond to one of the possibilities given in *X* in the contexts listed in the rule.  In other words, *X.s - X* may not occur in any of the contexts given by the rule.  Thus *X <= LC _ RC* is equivalent to *X.s - X /<= LC _ RC*

**<=>**
    Combination of the => and <= rules.

**/<=**
    An **exclusion rule** says that any expression matching the center of the rule may not occur in any of the contexts given by the rule.


--------------------
Testing of the rules
--------------------

For all types of the rules, there is a straight-forward way to check whether the rules apply to the set of examples given to the compiler:  each rule must accept all examples.  Rules only affect examples where the centre of the rule (or the X part) is present.  The author must write (and tune) the rules so that all such examples are accepted.

The compiler can also test rules against so called negative examples as is discussed in :doc:`twdiscov`.  The negative examples are derived from the given set of examples by distorting them a bit.

For a context requirement rule, this means that one must find contexts other than the ones whre X actually occurs in the set of examples.  Here we choose to seach occurrences where something like X occurs.  The program considers all examples where an Y in X.m occurs.  In these contexts, one replaces that center Y with the center of the rule, X.  From this collection of distorted examples, one still removes any examples that happen to be in the original set of examples.  If the compiled rule accepts any examples in this difference, the compiler reports them as a warning.  If a rule has a too permissive context, then all positive examples are still accepted.  But then, some negative examples are also accepted.  A listing of such negative examples is usually quite useful information for improving the rule.

For an output coercion rule (``<=``), we create the set of negative examples by first finding all examples where X occurs, and replace them with all strings Y in X.m.  From the set of distorted examples we, again, subtract any examples which are in the original set of examples.  This difference is the set of negative examples for an output coercion rule.  The rule is expected to discard all such examples, and the compiler can list any negative example which the rule accepts.

For an input coercion rule (``<--``) the building of negative examples is similar, but instead of using X.m one uses X.s.

In order to make testing against negative examples general, one would need a different version of the context requirement rule (=>) which could be (``-->``).  That rule would compile the same way as the normal one but it would have a different set of negative examples for testing it.  Obviously, the double arrow rule ought to have, then, a counterpart (``<-->``) too.

