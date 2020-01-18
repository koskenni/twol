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

1. Each :term:`raw morphophoneme` is scored according to the set of phonemes (and the zero) which are present in it.  The score for the alignment is the sum of the scores of all its raw morphophonemes.  Only the candidates with the best score are kept.

2. The syllable structure of the alignment is considered.  Those having a smaller number of syllables are preferred and those having a greater number are discarded.

3. Among otherwise equally good alignments, those alignments where the zeros occur more to the right are preferred.  The best of remaining alignments is the result.


A simpler and more versatile version of for aligning just two words or morphs is described in [koskenniemi2013b]_.


Installing
==========

One may install the programs for alignment as a Python package called ``twolalign`` by using ``pip3 install --upgrade twolalign`` or equivalently with the Python itself::

  $ python3 -m pip install --user --no-cache-dir --upgrade twolalign

Installing the package this way makes a few command line scripts that can executed as if they were executable programs, in particular: ``twol-multialign`` and ``twol-aligner``.  The available parameters for these, and other scripts in the package, can be seen by giving the ``--help`` option to the script.

Otherwise, you may also just clone the github project ``https://github.com/koskenni/alignment`` to your personal Linux or Mac.  On a Linux machine, you can do that by::

  git clone git@github.com:koskenni/alignment.git


Standalone use
==============

The help message::

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

  $ python3 multialign.py
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

  $ python3 multialign.py --layout horizontal
  saapas saappaa saappa                           (first input line)
  s a a p Øpp a sØØ ØaØ


Use from another program
========================

You can e.g.::

  import multialign
  morpheme = "MIES"
  words = ["mies", "miehe", "mieh"]
  aligned_sym_seq = multialign.aligner(words, 1, morpheme)
  print(aligned_sym_seq)
  
and it would print::
  
  ['mmm', 'iii', 'eee', 'shh', 'ØeØ']
  

Functions of the ``multialign`` module
======================================

.. automodule:: multialign
   :members:


