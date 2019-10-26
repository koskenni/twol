# twol
Compiler and other tools for two-level morphology

This repository contains various tools for *Simplified Two-level morphology* which is a revised form of the original two-level morphology as implemented in hfst-twolc (see https://github.com/hfst/hfst/wiki/HfstTwolc).  The tools are implemented in Python and many of them use the HFST finite-state transducer tools, especially its Python version (see https://github.com/hfst/python).

The tools in this repository include:

1. A compiler *twol.py* which reads in a set of examples and a grammar file containing two-level rules.  The compiler parses the rules, compiles them and tests them against the examples. The compiler can write the compiled rules as binary finite-state transducers into a file which can be used with the HFST command line tools.
2. Methods for aligning words or stems. These are useful for defining underlying representations of lexical entries.  Morphophonemes in the entries are a result of the alignment process.
3. Documentation of the methods and the programs.  The source text for documentation is in the docs directory and a human readable set of interlinked documents is available at readthedocs
