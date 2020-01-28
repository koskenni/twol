# twol: Compiler and other tools for two-level morphology

**NOTE:** the programs are under development and many of them may not
  work as expected

This repository contains various tools for *Simplified Two-level
morphology* which is a revised form of the original two-level
morphology as implemented in hfst-twolc (see
https://github.com/hfst/hfst/wiki/HfstTwolc).  The tools are
implemented in Python and many of them use the HFST finite-state
transducer tools, especially its Python version (see
https://github.com/hfst/python).

The tools in this repository include:

1. A compiler *twol.py* which reads in a set of examples and a grammar
   file containing two-level rules.  The compiler parses the rules,
   compiles them and tests them against the examples. The compiler can
   write the compiled rules as binary finite-state transducers into a
   file which can be used with the HFST command line tools.

2. Methods for aligning words or stems. These are useful for defining
   underlying representations of lexical entries.  Morphophonemes in
   the entries are a result of the alignment process.

3. Documentation of the methods and the programs.  The source text for
   documentation is in the docs directory and a human readable set of
   interlinked documents is available at readthedocs


# twol-comp: Compiler and rule tester for two-level rules

The compiler is based on a well-chosen set of examples against which
the rules will be immediately tested.  Rules have no significance
before we have the examples.  One way to produce a set of two-level
examples is the alignment programs which are described later on in
this file.  The idea of simplified two-level model  is described in
https://pytwolc.readthedocs.io/en/latest/intro.html and the use of the
``twpö-comp`` program is described in
https://pytwolc.readthedocs.io/en/latest/compiletest.html and some
other chapters there.


# Letter by letter alignment of words

Methods for careful letter by letter alignment for e.g. cognate words
in historical linguistics or when matching different stems of a words
with each other. Alignment adds zero symbols where necessary in order
to match words or stems that differ in length. Alignment is
particularly important in two-level morphology because the alignment
determines what morphophonemes there will be.

In the present context, alignment is the process of inserting some
zero symbols in the words so that the letters or phonemes in the
corresponding positions of the words are phonologically as similar as
possible, e.g. a Finnish word "kieli" and an Estonian word "keel"
could be aligned by inserting a zero symbol 'Ø':

    k i e l i
    k e e l Ø

Now there are pairs of identical phonemes (k:k, e:e and l:l) and one
modification of a vowel (i:e) and the deletion of a word-final vowel
(i:Ø).

There are stand-alone Python 3 programs which can be used from
command-line for aligning individual words:

1. ``twol-aligner`` and ``metrics.py`` with which you can compare
   cognate words of two languages. The latter reads an alphabet
   definition and writes a weighted finite-state transducer (WFST) which
   the former program needs for the concrete alignment.

2. ``twol-multialign`` compares two or more corresponding words or
   morphs and aligns them.

There is a suite of stand-alone programs for building morphophonemic
representations of morphemes.  The input consists of inflected word
forms given as a table where individual cells contain the word forms
where morph boundaries are indicated.  The forms with the same stem
are given as a row of the table and different forms correspond to the
columns of the table.  The programs are:

3. ``twol-table2words`` reads in a table in CSV (Comma Separated
   Values) format and writes it in a one word form per line CSV format.

4. ``twol-words2zerofilled`` reads in the output of the above program
   and aligns the morphs, i.e. stems of the same lexeme with each other
   and alternate forms of affixes of the same grammatical form with each
   other.  Aligned result is a table where the morphs include the
   optimally inserted zeros as an additional column in the CSV format
   file.

5. ``twol-zerofilled2raw`` reads in the output of the above program
   and produces an additional column which contains raw morphophonemic
   forms of each morpheme.

6. ``twol-raw2named`` reads in the output of the above program and a
   table of user-given shorter names for some raw morphophonemes and
   writes out the examples as two-level symbol pairs, one example per
   line.  The examples now consist of a sequence of symbol pairs where
   the first component of a pair is the morphophoneme and the second
   component is the surface character.  This file is used by the
   two-level compiler in conjunction with the rules which the linguist
   now can start to design.

More information on these programs can be found at:
https://pytwolc.readthedocs.io/en/latest/morphophon.html and by
starting the programs with a ``--help`` option.

## Licenses

The programs aligner.py, charmetric.py and multialign.py are written
by Kimmo Koskenniemi alone and he has the copyright to these
programs. The programs are free software according to the GNU General
Public License Version 3, 29 June 2007, see LICENSE.txt in this
repository or https://www.gnu.org/licenses/gpl-3.0.en.html for the
full text of the license.

The file tyveb-n-stems.text is derived from a file available at the
Institute of Estonian Language (IEL)
https://www.eki.ee/tarkvara/perlmorf/tyvebaas.pmf.  The license for
the file can be seen at https://www.eki.ee/eki/licence.html
