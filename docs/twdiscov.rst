.. _discovery:

===============================
Discovering raw two-level rules
===============================

The ``twdiscov.py`` program reads in a set of two-level examples which consist of space-separated :term:`pair symbols <pair symbol>` and the program produces tentative two-level rules for all :term:`morphophonemes <morphophoneme>` in the examples or just for a given morphophoneme.  Even when processing raw rules for all morphophonemes, the program proceeds one morphophoneme at a time.

The method is based on producing positive and negative examples which are specific to one morphophoneme.  The *positive examples* consist of all examples which contain that morphophoneme.

The *negative examples* are made from the positive ones by distorting the occurrences of the morphophoneme.  Each occurrence is replaced by all correct and incorrect pairs of that morphophoneme.  This results in all negative examples we need, but it also produces some correct examples.  Thus, from this preliminary set, the program subtracts all positive examples and then it has the final set of negative examples for this morphophoneme.

The script finds rule contexts incrementally.  The initial set of context is made out of the examples as such.  Such a rule trivially accepts all examples and rejects all negative examples.  The idea of the algorithm is to shorten the contexts step by step.  The shorter contexts still accept the positive examples but they do not necessarily reject all negative ones.  As long as they do reject, the process goes on.  One side is shortened first and then the other.

The program suggests reasonable raw rules for phenomena where the condition is strictly local, e.g. stem-final vowel alternations and also for consonant gradation in Finnish.  On the other hand, long distance phenomena e.g. vowel harmony cannot be summarized properly by this method as is shown below.

The program only produces ``=>`` and ``/<=`` types of rules.  This is not a limitation which would restrict the phenomena which can be expressed.  Indeed, when some phenomena are optional, using just these two types of rules makes it easy to allow for free variation.

Enven in the best case, the rules can only be as good as the set of examples. If the examples are chosen in a disciplined and balanced manner, the program is expected to be useful and practical.  If alternations are only partly present in the set of examples, the proposed raw rules will be poor and may even be misleading.


Using ``twdiscov.py``
=====================

The input for this script must be in the same format as the examples given to the ``twol.py`` rule compiler and tester, e.g.::

  m ä {kØ}:k {ieeØ}:i
  m ä {kØ}:Ø {ieeØ}:e n GEN:Ø
  m ä {kØ}:Ø {ieeØ}:e s s {aä}:ä INE:Ø
  m ä {kØ}:k {ieeØ}:e n {aä}:ä ESS:Ø
  m ä {kØ}:Ø {ieeØ}:Ø i s s {aä}:ä PL:Ø INE:Ø
  k ä {tds}:s {ieeØ}:i
  k ä {tds}:d {ieeØ}:e n GEN:Ø
  k ä {tds}:d {ieeØ}:e s s {aä}:ä INE:Ø
  k ä {tds}:t {ieeØ}:e n {aä}:ä ESS:Ø
  k ä {tds}:s {ieeØ}:Ø i s s {aä}:ä PL:Ø INE:Ø
  l a s {iiie}:i
  l a s {iiie}:i n GEN:Ø
  l a s {iiie}:i s s {aä}:a INE:Ø
  l a s {iiie}:i n {aä}:a ESS:Ø
  l a s {iiie}:e i s s {aä}:a PL:Ø INE:Ø
  l a {kØ}:k {iiie}:i
  l a {kØ}:Ø {iiie}:i n GEN:Ø
  l a {kØ}:Ø {iiie}:i s s {aä}:a INE:Ø
  l a {kØ}:k {iiie}:i n {aä}:a ESS:Ø
  l a {kØ}:Ø {iiie}:e i s s {aä}:a PL:Ø INE:Ø

The program collects the input and the output alphabets and the allowed symbol pairs from the examples, thus no other definitions are needed.  The program produces output such as::

   $ python3.5 ../twdiscov.py demo-raw.pstr
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
	_ {ieeØ}:e n GEN:Ø ;
   {tds}:s /<=
	_ {ieeØ}:e ;
   {tds}:t =>
	_ {ieeØ}:e n {aä}:ä ;

In the output, you can see that the rules for ``{aä}``, i.e. vowel harmony, are fairly useless, even if they are correct for the input data.  On the other hand, the rules for stem final vowel aternations for ``{ieeØ}`` and ``{iiie}`` are almost correct and general.  So are the rules for consonant gradation ``{kØ}`` and the slightly more complicated ``{tds}`` alternation.

Functions of the ``twdiscov`` module
====================================

.. automodule:: twdiscov
   :members:
