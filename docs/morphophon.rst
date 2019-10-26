.. _representations:

==============================
Morphophonemic representations
==============================

In linguistics, we say that word forms consist of :term:`morphs <morph>`, which are sequences of :term:`phonemes <phoneme>` and which have a meaning.  E.g.: a Finnish word form ``mäki`` consists just of the stem morph, 'a hill', whereas ``mäessä`` could be broken into two morphs::

  mäe  - 'a hill' - MÄKI
  ssä  - inessive

Another word form ``mäissä`` could be segmented into three morphs::

  mä   - 'a hill' - MÄKI
  i    - plural
  ssä  - inessive

Our goal is to find a common representation for morphs of the same :term:`morpheme`.  For the stem variants ``mäki``, ``mä`` and ``mäke`` we could establish a single form ``m ä {kØ} {ieØ}`` which could serve as the lexical entry for the morpheme MÄKI, 'a hill'.

In the following, a method is presented for constructing such a :term:`morphophonemic representation` out of a table of segmented word forms.  Four rather straight forward scripts are given.  The process is mostly automatic but human intervention is needed in:

- collecting model words and arranging as a table with columns for different relevant forms and rows for different lexemes

- segmenting the word forms so that their morphs are separated e.g. with a period

- renaming the automatically produced raw morphophonemes

The process consists of four scripts:

The input for the first step is a CSV table which one can produce using a spreadsheet proghram and by saving the table as :term:`CSV` file, e.g.::

   ID,STM,STM INE,STM ESS,STM PL INE
   MÄKI,mäki,mäe.ssä,mäke.nä,mä.i.ssä
   KÄSI,käsi,käde.ssä,käte.nä,käs.i.ssä
   LASI,lasi,lasi.ssa,lasi.na,lase.i.ssa
   LAKI,laki,lai.ssa,laki.na,lae.i.ssa

parad2words.py
==============

This script reads in a paradigm table of word forms and writes the data in a format where each word form is on line of its own.  Both the input table and the output file are in the CSV format.  Output contains two fields, e.g.::

     MORPHEMES,MORPHS
     MÄKI,mäki
     MÄKI INE,mäe.ssä
     MÄKI ESS,mäke.nä
     MÄKI PL INE,mä.i.ssä
     KÄSI,käsi
     KÄSI INE,käde.ssä
     KÄSI ESS,käte.nä
     KÄSI PL INE,käs.i.ssä
     LASI,lasi
     LASI INE,lasi.ssa
     LASI ESS,lasi.na
     LASI PL INE,lase.i.ssa
     LAKI,laki
     LAKI INE,lai.ssa
     LAKI ESS,laki.na
     LAKI PL INE,lae.i.ssa

words2zerofilled.py
===================

This script reads data in the above CSV format produced either by the ``paratab2segcsv.py`` program or directly by the user.  The script aligns the variants of each morpheme and writes a CSV file augmented with the aligned i.e. zero-filled example word forms.  The :doc:`alignment` is accomplished by the ``multialign.py`` module, see :py:mod:`multialign`. The output contains the fields in the input and the zero-filled word forms as the third field, e.g.::

     MORPHEMES,MORPHS,ZEROFILLED
     MÄKI,mäki,mäki
     MÄKI INE,mäe.ssä,mäØe.ssä
     MÄKI ESS,mäke.nä,mäke.nä
     MÄKI PL INE,mä.i.ssä,mäØØ.i.ssä
     KÄSI,käsi,käsi
     KÄSI INE,käde.ssä,käde.ssä
     KÄSI ESS,käte.nä,käte.nä
     KÄSI PL INE,käs.i.ssä,käsØ.i.ssä
     LASI,lasi,lasi
     LASI INE,lasi.ssa,lasi.ssa
     LASI ESS,lasi.na,lasi.na
     LASI PL INE,lase.i.ssa,lase.i.ssa
     LAKI,laki,laki
     LAKI INE,lai.ssa,laØi.ssa
     LAKI ESS,laki.na,laki.na
     LAKI PL INE,lae.i.ssa,laØe.i.ssa

zerofilled2raw.py
=================

This script reads in the aligned example words from the preceding step and constructs a raw morphophonemic representation for each example word.  Output contains the three fields in the input and a new one, the raw morphophonemic representation of the word form, e.g.::

     MORPHEMES,MORPHS,ZEROFILLED,RAW
     MÄKI,mäki,mäki,m ä {kØkØ} {ieeØ} 
     MÄKI INE,mäe.ssä,mäØe.ssä,m ä {kØkØ} {ieeØ} s s {aä}
     MÄKI ESS,mäke.nä,mäke.nä,m ä {kØkØ} {ieeØ} n {aä}
     MÄKI PL INE,mä.i.ssä,mäØØ.i.ssä,m ä {kØkØ} {ieeØ} i s s {aä}
     KÄSI,käsi,käsi,k ä {sdts} {ieeØ} 
     KÄSI INE,käde.ssä,käde.ssä,k ä {sdts} {ieeØ} s s {aä}
     KÄSI ESS,käte.nä,käte.nä,k ä {sdts} {ieeØ} n {aä}
     KÄSI PL INE,käs.i.ssä,käsØ.i.ssä,k ä {sdts} {ieeØ} i s s {aä}
     LASI,lasi,lasi,l a s {iiie} 
     LASI INE,lasi.ssa,lasi.ssa,l a s {iiie} s s {aä}
     LASI ESS,lasi.na,lasi.na,l a s {iiie} n {aä}
     LASI PL INE,lase.i.ssa,lase.i.ssa,l a s {iiie} i s s {aä}
     LAKI,laki,laki,l a {kØkØ} {iiie} 
     LAKI INE,lai.ssa,laØi.ssa,l a {kØkØ} {iiie} s s {aä}
     LAKI ESS,laki.na,laki.na,l a {kØkØ} {iiie} n {aä}
     LAKI PL INE,lae.i.ssa,laØe.i.ssa,l a {kØkØ} {iiie} i s s {aä}

The program, in principle, construct the morphophonemes just by listing the alternating phonemes as a sequence in curly braces.  In real scale paradigms, this would result in many more morphophonemes than what is necessary.  On the other hand, the program could treat the alternations just as sets, which would result in a small set of morphophonemes.  Unfortunately, in real cases, some of these small sets would simplify too much.  E.g. ``kalsium<>`` - ``kalsium<i>n`` - ``kalsium<e>ja`` represents the same kind of alternation between ``i``, ``e`` and ``Ø`` as ``mäki`` but in a clearly different configuration.

Thus, the construction is made according to a user given set of *principal forms* (or principal parts) i.e. a ordered subset of inflected forms.  In traditional grammars, the principal forms, are understood the forms out of which one can mechanically produce all other inflected forms.

The morphophonemes in affixes coud be constructed mechanically, but we meet similar problems there.  In order to keep the method simple, the script reads in an additional CSV file which explicitly gives the principal forms and the morphophonemic representations of the affixes.  For our demo example::

  "",+
  "INE",+
  "ESS",+
  "PL INE",+
  ,
  INE,s s {aä}
  ESS,n {aä}
  PL,i

The file lists the principal forms in lines where the second field is ``+``.  Note that the principal forms may consist of zero, one or more affix morphemes (i.e. their names).  The remaining lines have the affix name in the first field and its morphophonemic representation in the second field.  Note that each morpheme (name) has an affix of its own.  One may establish distinct names for grammatically identical but phonemically distinct affixes.  (In Finnish, e.g. some plural genitive endings are so different that one may treat them as different morphemes having slighty different names.)

raw2named.py
============

This script renames some raw morphophonemes of the example word forms and writes a file of examples where each example is a line of blank separated string of :term:`pair symbols <pair symbol>`.  Pair symbols are the newly renamed ones or if the raw symbol is not yet renamed, the pair symbol is the original raw one.  This file is suitable for the twol.py compiler as its example file.

The new names can be determined one by one.  The decisions made so far are stored in a CSV file with three columns:  the first is the inital raw name, the second is the now given new name for the morphophoneme, and the third column is for documentation, e.g.::

  {kØkØ},{kØ},la<k>i la<>in
  {sdts},{tds},kä<t>enä kä<d>essä kä<s>issä

Assigning names to raw morphophonemes is usually done with the aid of ``twdiscov.py``, see :doc:`/twdiscov`.  The rule discovery module helps to identify similar raw morphophonemes and to give a common name to them.  The output of this script is e.g.::

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

One may also write a two-level rule for such tentatively final morphophoneme and test the validity of the rule using ``twol`` rule compiler.  See separate documents for them.
