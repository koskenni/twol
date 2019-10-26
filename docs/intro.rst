==========================
Simplified two-level model
==========================

.. note:: The twol.py program is still under development and so is this documentation

The morphological two-level model dates back to [koskenniemi1983]_ and is characterized by the descritpion of phonological or
morphophonological alternations as a direct relation between the
surface forms and their underlying lexical or morphophonemic forms. It differs from the classical generative phonology by explaining the alternations using parallel rules rather than as a cascade of successive rules, see [karttunen1993]_ for a demonstration of this difference.  The differences between the traditional two-level rules and the rules in the simplified two-level model are discussed in detail in a separate section, see :doc:`differences`.

Two-level rules are useful for describing inflected word forms in language which have phonemic alternations.  In such languages, the shapes of stems and affixes vary depending on phonological context.  The two-level model assumes that there is an underlying morphophonemic representation (as in classical generative phonology) but all rules which are needed, operate in parallel rather than in sequence.

To construct a morphophonological description, one has do two important tasks: (1) to establish the underlying *representations* and (2) design *rules* which relate the underlying representations to the surface forms.  In the two-level model the representations are quite different from those in the standard generative phonology, i.e. they do not consist of plain phonemes.

------------
Overall plan
------------

The present approach is based on a *set of carefully selected examples* of word forms.  The set of examples ought to cover the phenomena which the rules are expected to govern.  If so, one may expect that the method described below will first produce *morphophonemic representations* for stems and affix morphemes and then a *two-level rule* for each morphophoneme which dictates in what contexts the morphophoneme may correspond to what surface symbols.  Each morphophoneme may be treated *separately* in an order which the linguist finds convenient.

This set of documents demonstrates methods and tools for:

1. Establishing the morphophonemic representations (almost mechanically) out of a table of inflectional paradigms.  The method and the tools are described in a separate part of this documentation: :ref:`representations`.

2. Finding raw candidates for the two-level rules.  The method and the use of the program is described in a separate part of this documentatio: :ref:`discovery`.

3. Authoring a two-level rule and testing it immediately.  The testing is has been improved so that it consists of two phases: (a) the rule is checked against the examples and the program reports any examples not accepted by the rule, and (b) a set of negative examples is generated from the positive ones and the program checks that the rule discards all of them.  The revised rule formalism is described in part :ref:`formalism`, the use of the compiler in part :ref:`compiling`.  For the interested reader, some details of the methods and algorithms of the compilation process are documented separately: :ref:technical.  The compiler can also test the whole rule grammar against examples.  When a rule has been written for all morphophonemes, the program can make a more comprehensive check that the grammar is complete and has all necessary constraints.

Various methods and programs programs have been developed in order to simplify the whole process of creating a morphological two-level grammar.  It can be summarized using the following steps:

1. A linguist selects a representative set of example words.

2. The linguist marks the morph boundaries in the example words.

3. A program aligns the morphs in the examples by adding zero symbols.  The zero-filled morphs are the same length and phonemes in corresponding positions are phonologically similar.

4. A program produces example words as sequences of pair-strings where the left component of each pair is a raw morphophoneme implied by the alignment.  This is the initial version of the example file for designing and testing rules.

5. Using a version of the example file, one selects one morphophoneme at a time and:

   a. Lets a program produce tentative raw two-level rules for the morphophoneme.

   b. The linguists renames the raw morphophoneme and possibly merges it with some similar raw morphophonemes, and thus produces a revised version of the example file.

   c. The linguist tunes the raw two-level rule into a more general version when there appears to be need.

   d. A program compiles the rule and produces a set of positive and a set of negative test cases.  The program checks that all positive examples pass the rule and that all negative examples are rejected.  The program reports any failures.

   e. If all tests passed for this morphophoneme, proceed to the next morphophoneme.  If rejected positive or accepted negative examples were reported, check and revise the rules (or possibly the examples) and repeat from step (c).

When the process is complete, we have a set of two-level rules which accept all our examples and probably a large set of other word forms with similar morphophonemic alternatilns.



.. _examples:

-----------------------------------
Examples as strings of pair symbols
-----------------------------------

The simplified two-level model is heavily based on examples which are selected and edited before any rules are considered and before one starts to write the first rule.  The set of examples defines the possible correspondences or possible phoneme alternations; even the possible surface symbols and the set of morphophonemes is defined implicitly by the set of examples.

The examples are given as a file where each line is a string of *pair symbols*, e.g.::

  k a t {tØ}:Ø o l l {aä}:a

Here we have eight pair symbols, six of them are abbreviations, e.g. ``k`` stands for ``k:k`` and ``a`` for ``a:a``.  The remaining two pair symbols consist each of two symbols: a morphophonemic symbol ``{tØ}`` or ``{aä}`` combined with a surface symbol ``Ø`` or ``a``.  Another way of representing the examples would be them on two rows::

  k  a  t {tØ} o  l  l  {aä}
  k  a  t   Ø  o  l  l   a

The upper line is the morphophonemic representation of the example word form, and the lower line is the surface representation of it.  Note that in the examples, the two representations always are of the same length and a zero symbol (Ø) is inserted when necessary.  In the above example, the ultimate surface form consists of only seven sybols: ``k a t o l l a``.  Within the examples and in the rules, these zeros always expliciltly present.

There is yet another form in which the examples are represented, i.e. as a pair of strings and then the strings are given without spaces, e.g.::

  ka{tØ}oll{aä}:katØolla

One can readily see that the three ways to represent examples are equivalent.  Examples are edited as a text file, but for further processing, they are compiled into a FST using the ``ex2fst`` module.


.. _rule-formalism:

------------------------------------------------
Rule formalism in the simplified two-level model
------------------------------------------------

The simplified two-level grammar consists of one or more lines where each line may be either a *definition*, a *rule* or just a *comment*.  Definitions and rules are made out of *regular two-level expressions*.  Comment lines or empty lines are ignored when the grammar is compiled into finite-state transducers (FSTs).  Comment lines start with an exclamation mark (!) at the first non-blank column, e.g.::

  ! trisyllabic word structure
 
Regular two-level expressions
=============================

The set of possible symbol pairs comes from the set of previously edited examples.  The rules and the two-level regular expressions introduce no correspondences beyond those which occur in the examples.

The two-level regular expressions (TLREs) can be:



Definitions
===========

A definition assigns a name for a regular two-level expressionn.

.. warning:: The program is under development and it may tilt!


----------
References
----------

.. [koskenniemi1983] Kimmo Koskenniemi, 1983,
		     *Two-level Morphology: A General Computational
		     Model for Word-Form Recognition and Production*,
		     University of Helsinki, Department of General
		     Linguistics, Publications, Number 11.  160 pages.

.. [karttunen1987] Lauri Karttunen and Kimmo Koskenniemi and
		   Ronald M. Kaplan, 1987:
		   "A compiler for two-level phonological rules",
		   in M. Dalrymple, R. Kaplan, L. Karttunen,
		   K. Koskenniemi, S. Shaio and M. Wescoat, editors,
		   *Tools for Morphological Analysis*, pp. 1-61,
		   Center for the Study of Language and Information,
		   Stanford University, Vol. 87-108, CSLI Reports,
		   Palo Alto, California, USA.

.. [karttunen1993] Lauri Karttunen, 1993: "Finite-state Constraints",
		   in *Proceedings of the International Conference on
		   Current Issues in Computational Linguistics*, June
		   10-14, 1991.  Universiti Sains Malaysia, Penang,
		   Malaysia, pp. 173-194.

.. [koskenniemi2013b] Kimmo Koskenniemi, 2013: "Finite-state relations
		      between two historically closely related
		      languages" in *Proceedings of the workshop on
		      computational historical linguistics at NODALIDA
		      2013*, May 22-24, 2013, Oslo, Norway, NEALT
		      Proceedings Series 18, number 87, pages 53-53,
		      Linköping University Electronic Press, ISSN
		      1650-3740,
		      http://www.ep.liu.se/ecp/article.asp?issue=087\&article=004

.. [koskenniemi2017] Kimmo Koskenniemi, 2017: "Aligning phonemes using
                  finte-state methods", in *Proceedings of the 21st
                  Nordic Conference on Computational Linguistics*,
                  May, 2017, Gothenburg, Sweden, Association for
                  Computational Linguistics, pages 56-64,
                  http://www.aclweb.org/anthology/W17-0207

.. [KSK] Suomen kielen käänteissanakirja / Reverse dictionary of Modern Standard Finnish.
	 Compiled by Tuomo Tuomi.  SKS.

.. [NS] Nykysyomen Sanakirja, 1951-1961, Edited by Suomalaisen
	 Kirjallisuuden Seura, published by WSOY.

.. [NSSL] Kotimaisten kielten keskuksen nykysuomen sanalista.
	  (A list of headwords and their inflection class numbers.)
	  http://kaino.kotus.fi/sanat/nykysuomi/
		  
.. [ylijyrä2006] Anssi Yli-Jyrä and Kimmo Koskenniemi, 2006: "Compiling
		 Generalized Two-Level Rules and Grammars" in T.
		 Salakoski et al. (Eds.): *FinTAL 2006*, LNAI 4139,
		 pp. 174–185.

..
    bibliography:: kmkbib.bib
