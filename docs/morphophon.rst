.. _representations:

==============================
Morphophonemic representations
==============================

In linguistics, we say that word forms consist of :term:`morphs <morph>`, which are sequences of :term:`phonemes <phoneme>` and which have a meaning.  E.g.: a Finnish word form ``mäki`` consists just of the stem morph, 'a hill', whereas ``mäellä`` 'in a hill' could be broken into two morphs::

    mäe       llä
    MÄKI       INE
    'hill'    'in'
  
Here ``MÄKI`` stands for the stem morpheme and ``INE`` for inessive case.  Another word form ``mäissä`` could be segmented into three morphs::

    mä        i         ssä 
    MÄKI      PL        INE
    'a hill'  'plural'  'in'    

Our goal is to find a common representation for morphs of the same :term:`morpheme`.  For the stem variants ``mäki``, ``mä`` and ``mäke`` we could establish a single form ``m ä {kØ} {ieØ}`` which could serve as the lexical entry for the morpheme MÄKI, 'a hill'.

In the following, a method is presented for constructing such a :term:`morphophonemic representation` out of a table of segmented word forms.  Four rather straight forward scripts are given.  The process is mostly automatic but human intervention is needed in:

- collecting model words and arranging as a table with columns for different relevant forms and rows for different lexemes

- segmenting the word forms so that their morphs are separated e.g. with a period

- renaming the automatically produced raw morphophonemes

The process consists of four scripts and this chapter walks through these steps with a simple example file.

The input for the first step is table which one can produce using a spreadsheet and we show it here first as:

  +------+------+----------+----------+------------+
  | ID   | STM  | STM.INE  | STM.ESS  | STM.PL.INE |
  +======+======+==========+==========+============+
  | MÄKI | mäki | mäe.ssä  | mäke.nä  | mä.i.ssä   |
  +------+------+----------+----------+------------+
  | KÄSI | käsi | käde.ssä | käte.nä  | käs.i.ssä  |
  +------+------+----------+----------+------------+
  | LASI | lasi | lasi.ssa | lasi.na  | lase.i.ssa |
  +------+------+----------+----------+------------+
  | LAKI | laki | lai.ssa  | laki.na  | lae.i.ssa  |
  +------+------+----------+----------+------------+

In the table, ``STM``  stands for the stem morph and ``ID`` for the column for the names of stem morphemes.  The twol programs read and write all tables in Comma Separated Value (:term:`CSV`) format  such as `demo-table.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/demo-table.csv>`_::

   ID,   STM,  STM.INE,  STM.ESS, STM.PL.INE
   MÄKI, mäki, mäe.ssä,  mäke.nä, mä.i.ssä
   KÄSI, käsi, käde.ssä, käte.nä, käs.i.ssä
   LASI, lasi, lasi.ssa, lasi.na, lase.i.ssa
   LAKI, laki, lai.ssa,  laki.na, lae.i.ssa

twol-table2words
================

The command::

    $ twol-table2words demo-table.csv demo-words.csv

reads in a paradigm table `demo-table.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/demo-table.csv>`_ of word forms and writes the data again in CSV format as a file `demo-words.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/kskn-words-orig.csv>`_ but now so that each word form is on line of its own.  Both the input table and the output file are in the CSV format.  Output contains two fields, e.g. (where some spaces have been inserted after comma to make the tables more readable)::

     MORPHEMES,   MORPHS
     MÄKI,        mäki
     MÄKI.INE,    mäe.ssä
     MÄKI.ESS,    mäke.nä
     MÄKI.PL.INE, mä.i.ssä
     KÄSI,        käsi
     KÄSI.INE,    käde.ssä
     KÄSI.ESS,    käte.nä
     KÄSI.PL.INE, käs.i.ssä
     LASI,        lasi
     LASI.INE,    lasi.ssa
     LASI.ESS,    lasi.na
     LASI.PL.INE, lase.i.ssa
     LAKI,        laki
     LAKI.INE,    lai.ssa
     LAKI.ESS,    laki.na
     LAKI.PL.INE, lae.i.ssa

twol-words2zerofilled
=====================

This step needs the CSV file `demo-words.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/kskn-words-orig.csv>`_ that was produced in the previous step but we also need a file which defines the alphabet used in the examples.  The definition gives the approximate sound features of the letters which represent the phonemes.  For this demo example there is one file `alphabet.text <https://raw.githubusercontent.com/koskenni/twol/master/test/align/alphabet.text>`_.  The alignment uses the alphabet file for determining how similar different phonemes are.  See more explanation of the alphabet definition file in the chapter :doc:`alignment`.

The step itself consists of the following command::

 $ twol-words2zerofilled demo-words.csv demo-zerofilled.csv \
                         alphabet.text

This script reads data in the above CSV format produced either by the ``twol-table2words`` program or directly by the user.  The script aligns the variants of each morpheme and writes a CSV file `demo-zerofilled.csv <https://github.com/koskenni/twol/blob/master/test/align/demo-zerofilled-orig.csv>`__ which is augmented with the aligned i.e. zero-filled example word forms.  The alignment is accomplished by the ``multialign.py`` module, see :doc:`alignment` and :py:mod:`multialign`. The output contains the fields in the input and the zero-filled word forms as the third field, e.g.::

     MORPHEMES,   MORPHS,     ZEROFILLED
     MÄKI,        mäki,       mäki
     MÄKI.INE,    mäe.ssä,    mäØe.ssä
     MÄKI.ESS,    mäke.nä,    mäke.nä
     MÄKI.PL.INE, mä.i.ssä,   mäØØ.i.ssä
     KÄSI,        käsi,       käsi
     KÄSI.INE,    käde.ssä,   käde.ssä
     KÄSI.ESS,    käte.nä,    käte.nä
     KÄSI.PL.INE, käs.i.ssä,  käsØ.i.ssä
     LASI,        lasi,       lasi
     LASI.INE,    lasi.ssa,   lasi.ssa
     LASI.ESS,    lasi.na,    lasi.na
     LASI.PL.INE, lase.i.ssa, lase.i.ssa
     LAKI,        laki,       laki
     LAKI.INE,    lai.ssa,    laØi.ssa
     LAKI.ESS,    laki.na,    laki.na
     LAKI.PL.INE, lae.i.ssa,  laØe.i.ssa

Here we can see why we need to have the same number of periods (.) in the column of MORPHEMES and in the column of MORPHS and actually in the original table.  The aligner now knows which parts of the word forms correspond to stems and what affixes.  With this information, the program can align allomorphs of each stem and of each affix separately.  The aligned morphs now contain some zeros so that the morphs of each morpheme are the same length, e.g. for MÄKI we have stems ``mäki``, ``mäØe``, ``mäke`` and ``mäØØ``.  The phonemes in the first position is constantly ``m``, in the second ``ä``, in the third alternating with ``k`` and ``Ø`` and in the fourth position alternating between ``i``, ``e`` and ``Ø``.  This is the information needed for constructing raw morphophonemes as we see in the next sub-section.


twol-zerofilled2raw
===================

In full scale processing, the tables might contain many more columns than are actually needed for determining the morphophonemic alternations in the stems.  We often need to select just a subset of the columns in the table.  In full scale tables, the sequence of alternating phonemes in the stems may follow the sequence of the columns in the table.  But, on the contrary, there are arbitrary many occurences of each affix and they are not in any particular order.  Thus, the processing needs still one small definition file ``demo-affixes.csv``.  The command for this step is::

  $ twol-zerofilled2raw demo-zerofilled.csv demo-raw.csv \
                        demo-affixes.csv

This command reads in the aligned example words file `demo-zerofilled.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/demo-zerofilled-orig.csv>`__ from the preceding step and constructs a raw morphophonemic representation for each example word.  It needs a small file `demo-affixes.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/demo-affixes.csv>`__ which will be discussed later on in this sub-section.

The output file `demo-raw.csv <https://raw.githubusercontent.com/koskenni/twol/master/test/align/demo-raw-orig.csv>`__ contains the three fields in the input and a fourth one, the raw morphophonemic representation of the word form, e.g.::

     MORPHEMES,   MORPHS,     ZEROFILLED, RAW
     MÄKI,        mäki,       mäki,       m ä {kØkØ} {ieeØ} 
     MÄKI.INE,    mäe.ssä,    mäØe.ssä,   m ä {kØkØ} {ieeØ} s s {aä}
     MÄKI.ESS,    mäke.nä,    mäke.nä,    m ä {kØkØ} {ieeØ} n {aä}
     MÄKI.PL.INE, mä.i.ssä,   mäØØ.i.ssä, m ä {kØkØ} {ieeØ} i s s {aä}
     KÄSI,        käsi,       käsi,       k ä {sdts} {ieeØ} 
     KÄSI.INE,    käde.ssä,   käde.ssä,   k ä {sdts} {ieeØ} s s {aä}
     KÄSI.ESS,    käte.nä,    käte.nä,    k ä {sdts} {ieeØ} n {aä}
     KÄSI.PL.INE, käs.i.ssä,  käsØ.i.ssä, k ä {sdts} {ieeØ} i s s {aä}
     LASI,        lasi,       lasi,       l a s {iiie} 
     LASI.INE,    lasi.ssa,   lasi.ssa,   l a s {iiie} s s {aä}
     LASI.ESS,    lasi.na,    lasi.na,    l a s {iiie} n {aä}
     LASI.PL.INE, lase.i.ssa, lase.i.ssa, l a s {iiie} i s s {aä}
     LAKI,        laki,       laki,       l a {kØkØ} {iiie} 
     LAKI.INE,    lai.ssa,    laØi.ssa,   l a {kØkØ} {iiie} s s {aä}
     LAKI.ESS,    laki.na,    laki.na,    l a {kØkØ} {iiie} n {aä}
     LAKI.PL.INE, lae.i.ssa,  laØe.i.ssa, l a {kØkØ} {iiie} i s s {aä}

The program, in principle, constructs the morphophonemes just by listing the alternating phonemes as a sequence in curly braces.  In real scale paradigms, this would result in many more morphophonemes than what is necessary.  On the other hand, the program could treat the alternations just as sets, which would result in a small set of morphophonemes.  Unfortunately, in real cases, some of these small sets would simplify too much.  E.g. ``kalsium<>`` - ``kalsium<i>n`` - ``kalsium<e>ja`` represents the same kind of alternation between ``i``, ``e`` and ``Ø`` as ``mäki`` but in a clearly different configuration.

Thus, the construction is made according to a user given set of :term:`principal forms` (or principal parts) i.e. a ordered subset of inflected forms.  In traditional grammars, the principal forms, are understood the forms out of which one can mechanically produce all other inflected forms.

The morphophonemes in affixes coud be constructed mechanically, but we meet similar problems there.  In order to keep the method simple, the script reads in an additional CSV file which explicitly gives the principal forms and the morphophonemic representations of the affixes.  For our demo example::

  "",     +
  INE,    +
  ESS,    +
  PL.INE, +
  INE,    s s {aä}
  ESS,    n {aä}
  PL,     i

The file lists the principal forms in lines where the second field is ``+``.  Note that the principal forms may consist of zero, one or more affix morphemes (i.e. their names).  The remaining lines have the affix name in the first field and its morphophonemic representation in the second field.  Note that each morpheme (name) has an affix of its own.  One may establish distinct names for grammatically identical but phonemically distinct affixes.  (In Finnish, e.g. some plural genitive endings are so different that one may treat them as different morphemes having slighty different names.)

twol-raw2named
==============

This script renames some raw morphophonemes of the example word forms and writes a file of examples where each example is a line of blank separated string of :term:`pair symbols <pair symbol>`.  Pair symbols are the newly renamed ones or if the raw symbol is not yet renamed, the pair symbol is the original raw one.  This file is suitable for the ``twol-comp`` compiler as its example file.

The linguist can determine the new names one by one.  The decisions made so far are stored in a CSV file with three columns:  the first is the inital raw name, the second is the now given new name for the morphophoneme, and the third column is for documentation, e.g.::

  {kØkØ},{kØ},la<k>i la<>in
  {sdts},{tds},kä<t>enä kä<d>essä kä<s>issä

The pair symbol string (PSTR) can be produced with the following command::

  $ twol-raw2named demo-raw.csv demo-renamed.pstr demo-newnames.csv

Assigning names to raw morphophonemes is usually done with the aid of ``twol-discov``, see :doc:`discovery`.  The rule discovery module also helps to identify similar raw morphophonemes and to give a common name to them.  The output of this script is e.g.::

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

One may also write a two-level rule for such tentatively final morphophoneme and test the validity of the rule using ``twol-comp`` rule compiler.  See separate documents for them.

There is a special option ``-F`` or ``--add-features`` in the ``twol-raw2named`` program which can be used in the rare cases where the phonological shapes of the affixes are not sufficient to deduce some alternations within the stem.  This option makes the program to add diacritical symbols to the end of the word.  These symbols indicate the grammatical form of the word form and they can be used in the two-level rule context.  Our example output would become as following, if the ``--add-features`` option is used::

   m ä {kØ}:k {ieeØ}:i
   m ä {kØ}:Ø {ieeØ}:e s s {aä}:ä INE:Ø
   m ä {kØ}:k {ieeØ}:e n {aä}:ä ESS:Ø
   m ä {kØ}:Ø {ieeØ}:Ø i s s {aä}:ä PL:Ø INE:Ø
   k ä {tds}:s {ieeØ}:i
   k ä {tds}:d {ieeØ}:e s s {aä}:ä INE:Ø
   k ä {tds}:t {ieeØ}:e n {aä}:ä ESS:Ø
   k ä {tds}:s {ieeØ}:Ø i s s {aä}:ä PL:Ø INE:Ø
   l a s {iiie}:i
   l a s {iiie}:i s s {aä}:a INE:Ø
   l a s {iiie}:i n {aä}:a ESS:Ø
   l a s {iiie}:e i s s {aä}:a PL:Ø INE:Ø
   l a {kØ}:k {iiie}:i
   l a {kØ}:Ø {iiie}:i s s {aä}:a INE:Ø
   l a {kØ}:k {iiie}:i n {aä}:a ESS:Ø
   l a {kØ}:Ø {iiie}:e i s s {aä}:a PL:Ø INE:Ø


Exercises
=========

In order to do these excercises, you must have a Python 3 installed (version at least 3.6) and install the twol-package. See instructions at https://github.com/koskenni/twol/wiki or at the end of the chapter :ref:`compiling`-

1. Test the existing ``demo`` example for creating morphophonemic representations for the example data in https://github.com/koskenni/twol/tree/master/test/align :
   Four files are needed: `alphabet.text <https://github.com/koskenni/twol/raw/master/test/align/alphabet.text>`__, `demo-affixes.csv <https://github.com/koskenni/twol/raw/master/test/align/demo-affixes.csv>`__, `demo-newnames.csv <https://github.com/koskenni/twol/raw/master/test/align/demo-newnames.csv>`__ and `demo-table.csv <https://github.com/koskenni/twol/raw/master/test/align/demo-table.csv>`__.  You can copy them through the links in the file names above, or you can go to the Github page and click the file name and after that the "Raw" button has a link to the source data.  Click that and then save the clean text version of the file.
   Run the commands that are given in sections 2.1, 2.2, 2.3 and 2.4 in this chapter.  Compare the results you get with the ones given in the above sections. 

2. Using a text editor, add two words in the demo-table.csv::

     KALA, kala, kala.n,  kala.ssa,  kala.na,  kalo.i.ssa
     MIES, mies, miehe.n, miehe.ssä, miehe.nä, mieh.i.ssä

   Run the programs again.  Study the alignment and the morphophonemes that you got.  Do you think that they are phonologically plausible?

3. Go to the directory where the alphabet.text file resides.  Run the multialigner as a separate program, but first with the help option::

     $ $ twol-multialign --help

   The program responds with a message that explains the parameters and switches (options) you must and may give to it.  Then::

     $ twol-multialign alphabet.text

   Thereafter you can give sets of space-separated lists of stems to  the program::

     hevonen hevose hevos

   The program responds with an alignment::

     hevonen
     hevoseØ
     hevosØØ

   Test this with five different stems.  You can test Finnish and Estonian words with the given alphabet file.  If you wish to test stems in other languages, you probably need to add some letters in the alphabet file, which you may easily do.  Note however, that if the orthography of the language is not phonemic (e.g. Chinese, or even English or French), there is not much point in the alignment.

4. Consider the Swedish strong verbs as given at `Wikipedia <https://sv.wiktionary.org/wiki/Appendix:Starka_verb>`__.

   - In Github, there is a verson of that table `svsv-table.csv <https://github.com/koskenni/twol/raw/master/test/align/svsv-table.csv>`__.  The CSV table has morph boundaries (``.``) in place.

   - Run the ``twol-table2words``, and correct any typos you might have made.  Discrepances between the numbers of dots (i.e. morphs) will be reported by the program.

   - Run the ``twol-words2zerofilled``.  Discrepances between the words and the alphabet are detected here by the program.

   - Run the ``twol-zerofilled2raw``.  Study the morphophonemes proposed by the program.  Are they acceptable?  The program makes good guesses, but it also makes mistakes.

   Run the ``twol-raw2renamed`` program so that you get a file of space-separated pair symbols ``svsv-renamed.pstr``.

   - Finally, run the ``twol-discov`` program in order to get tentative rules which account for the different surface shapes of the stems and the ending::

       twol-discov -s '{ieii}' svsv-renamed.pstr

     See the chapter :doc:`discovery` for more information on that program.   This gives two possible two-level rules for the raw morphophoneme ``{ieii}``::

       {ieii}:e =>
             _ g .#.,
             _ p .#.,
             _ t .#.,
             _ v .#. ;
        !                         .#.b<e>t.#.
        !                        .#.st<e>g.#.
        !                        .#.bl<e>v.#.
        !                       .#.skr<e>v.#.
        !                        .#.gr<e>p.#.
        {ieii}:i =>
             _ p i,
             _ t e,
             _ g i,
             _ t i,
             _ g {aØ}:a,
             _ t {aØ}:a,
             _ v {aØ}:a,
             _ p {aØ}:a,
             _ v e,
             _ g e,
             _ p e,
             _ v i ;
        !                        .#.bl<i>vit.#.
        !                        .#.st<i>gen.#.
        !                        .#.st<i>ga.#.
        !                         .#.b<i>tit.#.
        !                        .#.bl<i>va.#.
        !                       .#.skr<i>vit.#.
        !                        .#.gr<i>pit.#.
        !                        .#.gr<i>pa.#.
        !                         .#.b<i>ta.#.
        !                       .#.skr<i>ven.#.
        !                         .#.b<i>ten.#.
        !                        .#.st<i>git.#.
        !                       .#.skr<i>va.#.

     The lines starting with an exclamation mark (!) are just comments which give the actual example words where that realization of the morphophoneme is present.

     Your task as a computational linguist is to look at the two rules and propose a generalization, i.e. a more compact rule which would do the same thing but in a more general way.  Look at the contexts, if one could use a set of all vowels or all consonants instead of having individual konsonants like ``g``, ``p`` etc.  See wether the two rules could be merged into a single one.  Study the documentation of the two-level rules in :doc:`formalism`.

5. Study the raw morphophonemes of the preceding excercise and design a CSV file ``svsv-newnames`` which maps all all raw morphophophonemes to some cleaner and shorter forms.  Run the ``twol-discover`` again.  In case you are interested, you might continue by designing two-level rules for this small set of phenomena.

