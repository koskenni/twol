=========
Alignment
=========

This module aligns :term:`morphs <morph>` (or words) by inserting :term:`zero` symbols so that the phonemes of each morph correspond to each other, e.g. three morphs::

 'saapas', 'saappaa', 'saappa'

would be aligned by inserting some zeros resulting in::

  'saapØasØ', 'saappaØa', 'saappaØØ'

The essential goal when inserting the zeros is that the phonemes in the correspoinding positions of the zero-filled morphs would be phonologically similar.  In this example, the four first phonemes (``s``, ``a``, ``a``, ``p``) in the original morphs happen to be identical (and no zeros are needed).  The fifth is ``a`` or ``p`` which is not an acceptable correspondence.  The algorithm chooses to insert a zero to the first morph, so that we have a correspondence ``Ø-p-p``.  Consonants may not correspond to vowels (except for some semivowels).  All morphs must be made the same length, i.e. at least as long as the longest morph but perhaps even a bit longer.

Thus, some ways to insert zeros result in infeasible alignment and other result in possible alignments.  Some feasible alignments are evaluated as better than some others according to the phoneme correspondences the alignments imply.

The algorithm is described in some detail in [koskenniemi2017]_.  The present version proceeds in three steps:

1. Each :term:`raw morphophoneme` is scored according to the set of phonemes (and the zero) which are present in it.  The score for the alignment is the sum of the scores of all its raw morphophonemes.  Only the candidates with the best total score are kept.

2. The syllable structure of the alignment is considered.  Those having a smaller number of syllables are preferred and those having a greater number are discarded.

3. Among otherwise equally good alignments, those alignments where the zeros occur more to the right are preferred.  The best of remaining alignments is the result.


A simpler and more versatile version of for aligning just two words or morphs is described in [koskenniemi2013b]_.


Alphabet
========

The alignment is based on the similarities of phonemes.  Therfore a definition of the alphabet is obligatory.  The definition is a file which defines the letters in terms of their distinctive phonological features as in the International Phonetic Alphabet (IPA), see https://www.internationalphoneticalphabet.org/ for more information.  Here is a fairly extensive definition for Estonian alphabet::

   m  =  Bilabial, Voiced, Nasal,,,
   p  =  Bilabial, Unvoiced, Stop,,,
   b  =  Bilabial, Voiced, Stop,,,
   v  =  Labiodental, Voiced, Fricative,,,
   f  =  Labiodental, Unvoiced, Fricative,,,
   t  =  Dental, Unvoiced, Stop,,,
   z  =  Dental, Unvoiced, Affricate,,,
   s  =  Alveolar, Unvoiced, Sibilant,,,
   d  =  PostAlveolar, Voiced, Stop,,,
   n  =  PostAlveolar, Voiced, Nasal,,,
   r  =  PostAlveolar, Voiced, Trill,,,
   l  =  PostAlveolar, Voiced, Lateral,,,
   j  =  Palatal, Voiced, Approximant, SemiVowel, Front, Unrounded
   k  =  Velar, Unvoiced, Stop,,,
   g  =  Velar, Voiced, Stop,,,
   h  =  Glottal, Unvoiced, Fricative,,,
   
   Bilabial Labiodental Dental Alveolar PostAlveolar Palatal Velar Glottal = 50
   Bilabial Labiodental Dental Alveolar PostAlveolar = 30
   Bilabial Labiodental = 20
   Dental PostAlveolar = 20
   Alveolar PostAlveolar Palatal = 20
   Velar Bilabial = 20
   Velar Labiodental = 20

   Unvoiced Voiced = 20

   Stop Fricative Sibilant Affricate Trill Lateral Approximant Nasal = 70
   Stop Sibilant Fricative Affricate = 10
   Sibilant Nasal = 30
   Stop Nasal = 20
   Fricative Nasal = 20
   Stop Sibilant Fricative Lateral Trill = 40

   i  =  ,,, Close, Front, Unrounded
   ü  =  ,,, Close, Front, Rounded  #  Estonian ü, IPA y
   u  =  ,,, Close, Back, Rounded
   e  =  ,,, CloseMid, Front, Unrounded
   ö  =  ,,, CloseMid, Front, Rounded  #  IPA ø
   o  =  ,,, CloseMid, Back, Rounded
   õ  =  ,,, CloseMid, Back, Unrounded  #  Estonian õ, IPA ɤ
   ä  =  ,,, OpenMid, Front, Unrounded  #  IPA æ
   a  =  ,,, Open, Back, Unrounded  #  IPA ɑ

   SemiVowel Close CloseMid OpenMid Open = 70
   Close CloseMid OpenMid Open = 20
   Close CloseMid Open = 15
   Close CloseMid = 10
   CloseMid Open = 10
   OpenMid Open = 0
   SemiVowel Close = 10
   SemiVowel CloseMid = 60

   Front Back = 10

   Unrounded Rounded = 10

The lines with a symbol, equal sign and a comma separated list of six feature names define the *set of phonemes and their qualities*.  The alphabet is partitioned into *consonants* where the first three features must be present and into *vowels* where the last three features must be present. For *semivowels* or *approximants*, all six features are present.  Only these alternatives are allowed.  The features must belong consistently to one of these six positions.  Otherwise, the names used for the features can be freely chosen (although the IPA names are recommended).

The similarity of each pair or subsets of phonemes is defined by the rest of the lines in the example.  Consider a set of phonemes, e.g. ``{i, e}`` or equivalently a morphophoneme ``ie``.  In terms of features this morphophoneme is represented as::

  ({}, {}, {}, {Close, CloseMid}, {Front}, {Unrounded})

There are no consonantal features, i.e. the first three sets are empty and therefore have a zero weight.  The fifth and the sixth sets consist of just one feature, and their weights are also zero.  The fourth set has two features in it.  Its weight is determined by using the feature sets in the alphabet.  The set ``{Close, CloseMid}`` is a subset of four sets in the alphabet::
   
   SemiVowel Close CloseMid OpenMid Open = 70
   Close CloseMid OpenMid Open = 20
   Close CloseMid Open = 15
   Close CloseMid = 10

The sets define different weights, but the lowest weight is taken, thus the weight of this feature group is 10 and the total weight of the morphophoneme ``ie`` is 10.

When reading the alphabet file, the program computes the weights of all possible subsets and their weights of each of the six feature groups.  These pre-computed weights are then used for deciding which alignments are the best. 


Installing the package
======================

One may install the programs for alignment as a Python package called ``twolalign`` by using::

  $ pip3 install --user twolalign

or equivalently with the Python itself::

  $ python3 -m pip install --user twolalign

Installing the package this way makes a few command line scripts that can executed as if they were executable programs, in particular: ``twol-multialign`` and ``twol-aligner``.

If you have previously installed a version of ``twolalign`` and you wieh to replace it with a newer one, you can use an additional option ``--upgrade`` in the installation commands.

If you indend to participate in the development of these tools, you may also clone the github project ``twolalign`` to your personal Linux or Mac computer by::

  $ git clone git@github.com:koskenni/alignment.git



``twol-multialign``
===============

Befor using a command or script, one is advised first to ask it for help i.e. what the program will do and what kinds of parameters it needs, e.g.::

   $ twol-multialign --help
   usage: twol-multialign [-h] [-l {vertical,list,horizontal}] [-f] [-w]
                          [-c] [-v VERBOSITY] [-z ZEROS] alphabet

   positional arguments:
     alphabet              A file which defines the phonemes through their
                           distinctive features

   optional arguments:
     -h, --help            show this help message and exit
     -l {vertical,list,horizontal}, --layout {vertical,list,horizontal}
                           Output layout
     -f, --final           Prefer deletion at the end
     -w, --weights         Print the weight of the alignment
     -c, --comments        Copy input words to the output lines as comments
     -v VERBOSITY, --verbosity VERBOSITY
                           Level of diagnostic output
     -z ZEROS, --zeros ZEROS
                           Number of extra zeros allowed beyond the minimum

The module can be executed as a script.  The default is that the zero-filled aligned morphs are given in vertical layout::

  $ twol-multialign alphabet.text
  käsi käde käte kät käs                          (first input line)
  käsi
  käde
  käte
  kätØ
  käsØ
  
  saapas saappaa saappa                           (second input line)
  saapØasØ
  saappaØa
  saappaØØ


The results may printed in an alternative layout where the raw morphophonemes are explicitly given::

  $ twol-multialign --layout horizontal
  saapas saappaa saappa                           (first input line)
  s a a p Øpp a sØØ ØaØ


Using multialign from another program
=====================================

When the ``twolalign`` package has been installed, you can use the alignment from your own Python 3 program.  You can e.g.::

  from twolalign.multialign import aligner
  morpheme = "MIES"
  words = ["mies", "miehe", "mieh"]
  aligned_sym_seq = aligner(words, 1, morpheme)
  print(aligned_sym_seq)
  
and your program would print::
  
  ['mmm', 'iii', 'eee', 'shh', 'ØeØ']
  



