.. warning:: This document is under construction

.. _lexguessing:

========================
Guessing lexicon entries
========================

Here we assume that we already know quite a lot of the morphology and phonology of a language.  It is logical to first study the phonological alternations and the combining of affixes with a smaller set of examples.  Using such examples, we can construct the morphophonological representations that are needed for lexicon entries, see :ref:`representations` and :ref:`compiling`.

Populating the lexicon with enough adequate lexeme entries may often be a laborious task.  A native speaker might be able to inflect any given base form of a lexeme.  Many human-readable dictionaries provide numerical or other codes of :term:`inflection classes <inflection class>` for headwords or :term:`lemmas <lemma>`.  Such a code defines (more or less precisely) how the word must be inflected.  But, very few speakers can correctly give the inflection code for a given word.

This section discusses and presents methods for creating lexicon entries in two ways: (1) interactively in a dialogue between a speaker of the language and a program that is aware of the rules of morphophonemic alternations and inflectional patterns, and (2) blindly or in a batch mode combining the inflectional information with the occurrences of word forms in a large corpus.  Both approaches are based on regular expression patterns which describe the constraints that determine what shapes words in each inflection class may have.

Human-readable dictionaries often use quite large numbers of distinct inflection classes, e.g. Nykysuomen sanakirja (Dictionary of Modern Standard Finnish) uses 82 classes for nominal inflection and 45 for verbs.  The high numbers of classes comes from two independent factors: (a) stem final alternations (which depend on the shape of the end of the stem) and (b) constraints for affixing different allomorph endings (which depend on the syllable structure).


Patterns for inflection classes
===============================

Each inflection class can be described with one or more *patterns*.  Patterns are written as a CSV file, i.e. a table with a few columns:

    CONT
        Continuation class from which the affixes can be attached to the stems described by this pattern.  The continuation is the same thing as in LEXC entries.

    ICLASS
        Inflection class, e.g. the number used in a dictionary.

    MPHON
    A pattern which describes the lexicon entries may belong to this class (ICLASS).  The pattern resembles LEXC lexicon entries.  The pattern may be either a regular expression ``<...>`` or a single exceptional lexeme.  The regular expressions follow the XFST syntax used in LEXC except that curly braces ``{}`` are reserved for names of morphophonemes where they are not quoted with a percent sign ``%``, thus e.g. ``a:{ao}`` is just a symbol pair.  The input side of regular expressions is the base form of lexemes and the output side is the morphophonemic representation.  Epsilons **0** may be used when something in the base-form corresponds to nothing in the morphophonemic representation and vice versa.  (Be careful not to mix zero symbols ``Ø`` and epsilons **0**.  Remember that the zero symbol occurs only as a part of morphophonemes, e.g. ``a:{aØ}`` in these patterns, never by itself)

    COMMENT
        Comments do not affect the results but they are otherwise useful for the developer or maintainer of the patterns.


Regular expressions may consist of concatenation, Kleene star and plus, brackets for grouping, parenthesis for optionality, disjunction and intersection.  In particular, one may define expressions and use them in other definitions or patterns.  In the first column of a definition is a keyword ``Define``, in the second column is the name of the defined expression, and in the third column is the expression.

Compiling a guessing FST
========================



Interactive guessing
====================

Let us call GUESS the result of the compilation of the patterns together with the affixes and the rules.  It is a mapping from one word form into a set of tentative lexicon entries which could produce the given word form.  An interactive guesser can now prompt the human user for word forms of the desired lexical entry.  After the first form, there may be more than one alternative entries and then the user is prompted for a further form of the same lexeme.  The resulting lexicon entry must generate both forms.  If the result is now unique, the lexical entry is fully determined, but otherwise further forms of the lexeme are prompted for.


Interactive guessing with a corpus
==================================

The interactive guessing can be improved by combining it with data from a corpus.  Tentative lexical entries for a given word form can be evaluated directly by finding the sets of word forms in the corpus which would be generated by each of the candidate entries.  It is expected that the correct entry will be present as several forms in the corpus whereas the incorrect ones only in one or few forms.  The information present in the corpus can thus speed up the decision by ordering the candidate entries according to their quality so that the correct guess is the first one.

Batch guessing with a corpus
============================

Suppose we have a word list from a corpus.  This can be compiled into a FST, say WORDS.  We can compose this with GUESS in order to have a mapping from those word forms occurring into tentative lexical entries for each word form in question.  Let us call the result of this composition ENTRIES, and its inverse FORMS.  For each entry candidate, we have the number of word forms in the corpus that the entry could generate: len(FORMS[entry]).

We may enumerate all entries in the descending order according to the number of forms in the corpus that the entry generates.  For each entry e, in turn, consider each form it generates

    FORMS[e] = {f\ :sub:`1`, ..., f\ :sub:`k`\ }.

Consider all members e\ :sub:`ij` in ENTRIES[f\ :sub:`i`] (i = 1, ..., k) and compare the set FORMS[e] and FORMS[e\ :sub:`ij`]. If the former is a superset of the latter, then remove e\ :sub:`ij` as redundant because e explains every form in the corpus that e\ :sub:`ij` does and at least one form that e\ :sub:`ij` does not explain.

The removal of e\ :sub:`ij` is done by setting FORMS[e\ :sub:`ij`] = set() and by removing e\ :sub:`ij` from the set ENTRIES[f\ :sub:`i`].  Once an entry is found redundant, it will not compete with this or any other entries.

Entries with many forms in the corpus are likely to represent real lexemes.  The processes proceeds to entries with a smaller number of forms in the corpus reducing redundant entries.  Actually, the process can be repeated as long as it finds further redundant entries.

When we have removed all redundant entries, we are ready to start accepting entries as good candidates to be included in the lexicon.  Again, we start from entries which have the largest number of forms in the corpus.

A criterion for the acceptance could be just the number of forms the tentative entry explains.  Another criterion could test whether the set of forms in the corpus would be sufficient to uniquely determine the entry in the sense described above in the section for `Interactive guessing`_.

More problematic are cases where two entries X and Y compete so that X explains forms A+B and Y forms B+C where len(B) > len(A), len(C).

After accepting an entry e, one could go through all word forms w in FORMS[e].  From each x in ENTRIES[w], modify the sets FORMS[x] by removing w from it. 


Evaluatiing a guesser
=====================

Suppose we are guessing lexical entries out of a set W of words wi (i=1,..n) of a reference corpus where we have one entry ei given for each word in W.  Let E denote the set of all entries ej.   The algorithm that is evaluated produces for the set W a sequence of guessed entries Gk = [g1, g2, ... gk] .  Let us study the ratio qk = len(Gk INTERSECT E)/len(Gk) and its dependence on k.  If we fix a ratio r, say 75 %, then, with how large values of k the ratio rk remains below r.  For a fixed n size of W and a fixed value of r we get different ks for different versions of the guessing algorithm.

Finding weights for a guesser
=============================

Where we have word tokens and their analyses, i.e. base forms, features (FEAT) which include the part of speech (POS) and inflectional features (INFL).  Then, a rudimentary guesser will provide guessed entries for each word token and with the existing analyses.

In order to compare and match guesses and the analyses given in the corpus, one needs a function which maps the guessed enttry and FEAT to the base form and FEATs given in the corpus.  The base form of a guessed entry can be deduced using the generator.

From the guesses we can deduce which guess is correct and which ones are incorrect.  For FEATs we get statistics how often each FEAT is correct guesses and how often incorrect.  From a guessed morphophonemic entry we can deduce the pattern which has been used.  In this way, we get statistics for the patterns indicating how often each pattern succeeds or fails.

In order to find out which pattern is used in each guessed entry, one can insert a unique symbol at the end of each pattern, e.g. as::

   < (Cini) VoB+ NonGw u {tØthn} {ØeØØØ} =AIRUT=:0 0::30 > /s ;

In the guesses generated by such patterns, one would have this token in the analysis ready for making statistics.  This behaviour of entries2lexc.py must, of course, be optional and it will be used only for the tuning of weights.
